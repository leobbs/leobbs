package Net::DNS::Nameserver;
# $Id: Nameserver.pm,v 1.3 2002/05/31 08:46:47 ctriv Exp $

use Net::DNS;
use IO::Socket;
use IO::Select;
use Carp qw(cluck);
use strict;
use vars qw($VERSION);

$VERSION = $Net::DNS::Version;

use constant DEFAULT_ADDR => INADDR_ANY;
use constant DEFAULT_PORT => 53;

#------------------------------------------------------------------------------
# Constructor.
#------------------------------------------------------------------------------

sub new {
	my ($class, %self) = @_;

	my $addr = $self{"LocalAddr"} || inet_ntoa(DEFAULT_ADDR);
	my $port = $self{"LocalPort"} || DEFAULT_PORT;

	if (!$self{"ReplyHandler"} || !ref($self{"ReplyHandler"})) {
		cluck "No reply handler!";
		return;
	}

	#--------------------------------------------------------------------------
	# Create the TCP socket.
	#--------------------------------------------------------------------------

	print "creating TCP socket..." if $self{"Verbose"};

	my $sock_tcp = IO::Socket::INET->new(
		LocalAddr => $addr,
		LocalPort => $port,
		Listen	  => 5,
		Proto	  => "tcp",
		Reuse	  => 1,
	);

	if (!$sock_tcp) {
		cluck "couldn't create TCP socket: $!";
		return;
	}

	print "done.\n" if $self{"Verbose"};

	#--------------------------------------------------------------------------
	# Create the UDP Socket.
	#--------------------------------------------------------------------------

	print "creating UDP socket..." if $self{"Verbose"};

	my $sock_udp = IO::Socket::INET->new(
		LocalAddr => $addr,
		LocalPort => $port,
		Proto => "udp",
	);

	if (!$sock_udp) {
		cluck "couldn't create UDP socket: $!";
		return;
	}

	print "done.\n" if $self{"Verbose"};


	#--------------------------------------------------------------------------
	# Create the Select object.
	#--------------------------------------------------------------------------

	$self{"select"} = IO::Select->new;
	$self{"select"}->add($sock_tcp);
	$self{"select"}->add($sock_udp);

	#--------------------------------------------------------------------------
	# Return the object.
	#--------------------------------------------------------------------------

	my $self = bless \%self, $class;
	return $self;
}

#------------------------------------------------------------------------------
# make_reply - Make a reply packet.
#------------------------------------------------------------------------------

sub make_reply {
	my ($self, $query) = @_;

	my $reply;

	if ($query) {
		my $qr = ($query->question)[0];

		my $qname  = $qr ? $qr->qname  : "";
		my $qclass = $qr ? $qr->qclass : "ANY";
		my $qtype  = $qr ? $qr->qtype  : "ANY";

		$reply = Net::DNS::Packet->new($qname, $qclass, $qtype);

		if ($query->header->opcode eq "QUERY") {
			if ($query->header->qdcount == 1) {
				print "query ", $query->header->id,
			  ": ($qname, $qclass, $qtype)..." if $self->{"Verbose"};

		my ($rcode, $ans, $auth, $add) =
			&{$self->{"ReplyHandler"}}($qname, $qclass, $qtype);

		print "$rcode\n" if $self->{"Verbose"};

		$reply->header->rcode($rcode);

		$reply->push("answer",	   @$ans)  if $ans;
		$reply->push("authority",  @$auth) if $auth;
		$reply->push("additional", @$add)  if $add;
		}
		else {
			print "ERROR: qdcount ", $query->header->qdcount,
			  "unsupported\n" if $self->{"Verbose"};
		$reply->header->rcode("FORMERR");
		}
		}
		else {
			print "ERROR: opcode ", $query->header->opcode, " unsupported\n"
		  if $self->{"Verbose"};
			$reply->header->rcode("FORMERR");
		}
	}
	else {
		print "ERROR: invalid packet\n" if $self->{"Verbose"};
		$reply = Net::DNS::Packet->new("", "ANY", "ANY");
		$reply->header->rcode("FORMERR");
	}

	$reply->header->qr(1);
	$reply->header->ra(1);
	$reply->header->rd($query->header->rd);
	$reply->header->id($query->header->id);

	return $reply;
}

#------------------------------------------------------------------------------
# tcp_connection - Handle a TCP connection.
#------------------------------------------------------------------------------

sub tcp_connection {
	my ($self, $sock) = @_;

	print "TCP connection from ", $sock->peerhost, ":", $sock->peerport, "\n"
	  if $self->{"Verbose"};
		
	while (1) {
		my $buf;
		print "reading message length..." if $self->{"Verbose"};
		$sock->read($buf, 2) or last;
		print "done\n" if $self->{"Verbose"};

		my ($msglen) = unpack("n", $buf);
		print "expecting $msglen bytes..." if $self->{"Verbose"};
		$sock->read($buf, $msglen);
		print "got ", length($buf), " bytes\n" if $self->{"Verbose"};

		my $query = Net::DNS::Packet->new(\$buf);
		my $reply = $self->make_reply($query);
		my $reply_data = $reply->data;

		print "writing response..." if $self->{"Verbose"};
		$sock->write(pack("n", length($reply_data)) . $reply_data);
		print "done\n" if $self->{"Verbose"};
	}

	print "closing connection..." if $self->{"Verbose"};
	$sock->close;
	print "done\n" if $self->{"Verbose"};
}

#------------------------------------------------------------------------------
# udp_connection - Handle a UDP connection.
#------------------------------------------------------------------------------

sub udp_connection {
	my ($self, $sock) = @_;

	my $buf = "";
	my $peer_sockaddr = $sock->recv($buf, &Net::DNS::PACKETSZ);
	my ($peerport, $peeraddr) = sockaddr_in($peer_sockaddr);
	my $peerhost = inet_ntoa($peeraddr);

	print "UDP connection from $peerhost:$peerport\n" if $self->{"Verbose"};

	my $query = Net::DNS::Packet->new(\$buf);
	my $reply = $self->make_reply($query);
	my $reply_data = $reply->data;

	print "writing response..." if $self->{"Verbose"};
	$sock->send($reply_data) or die "send: $!";
	print "done\n" if $self->{"Verbose"};
}

#------------------------------------------------------------------------------
# main_loop - Main nameserver loop.
#------------------------------------------------------------------------------

sub main_loop {
	my $self = shift;

	local $| = 1;

	while (1) {
	print "waiting for connections..." if $self->{"Verbose"};
	my @ready = $self->{"select"}->can_read;

	foreach my $sock (@ready) {
			my $proto = getprotobynumber($sock->protocol);

			if (!$proto) {
				print "ERROR: connection with unknown protocol\n"
					if $self->{"Verbose"};
			}
			elsif (lc($proto) eq "tcp") {
				my $client = $sock->accept;
				$self->tcp_connection($client);
			}
			elsif (lc($proto) eq "udp") {
				$self->udp_connection($sock);
			}
			else {
				print "ERROR: connection with unsupported protocol $proto\n"
					if $self->{"Verbose"};
			}
		}
	}
}

1;

__END__

=head1 NAME

Net::DNS::Nameserver - DNS server class

=head1 SYNOPSIS

C<use Net::DNS::Nameserver;>

=head1 DESCRIPTION

Instances of the C<Net::DNS::Nameserver> class represent simple DNS server
objects.  See L</EXAMPLE> for an example.

=head1 METHODS

=head2 new

	my $ns = Net::DNS::Nameserver->new(
	LocalAddr	 => "10.1.2.3",
	LocalPort	 => "5353",
	ReplyHandler => \&reply_handler,
	Verbose		 => 1
	);

Creates a nameserver object.  Attributes are:

  LocalAddr		IP address on which to listen.	Defaults to INADDR_ANY.
  LocalPort		Port on which to listen.  Defaults to 53.
  ReplyHandler	Reference to reply-handling subroutine.	 Required.
  Verbose		Print info about received queries.	Defaults to 0 (off).

The ReplyHandler subroutine is passed the query name, query class,
and query type.	 It must return the response code and references
to the answer, authority, and additional sections of the response.
Common response codes are:

  NOERROR	No error
  FORMERR	Format error
  SERVFAIL	Server failure
  NXDOMAIN	Non-existent domain (name doesn't exist)
  NOTIMP	Not implemented
  REFUSED	Query refused

See RFC 1035 and the IANA dns-parameters file for more information:

  ftp://ftp.rfc-editor.org/in-notes/rfc1035.txt
  http://www.isi.edu/in-notes/iana/assignments/dns-parameters

The nameserver will listen for both UDP and TCP connections.  On
Unix-like systems, the program will probably have to run as root
to listen on the default port, 53.	A non-privileged user should
be able to listen on ports 1024 and higher.

Returns a Net::DNS::Nameserver object, or undef if the object
couldn't be created.

See L</EXAMPLE> for an example.	 

=head2 main_loop

	$ns->main_loop;

Start accepting queries.

=head1 EXAMPLE

The following example will listen on port 5353 and respond to all queries
for A records with the IP address 10.1.2.3.	 All other queries will be
answered with NXDOMAIN.	 Authority and additional sections are left empty.

  #!/usr/bin/perl -Tw
  
  use Net::DNS;
  use strict;
  
  sub reply_handler {
	  my ($qname, $qclass, $qtype) = @_;
	  my ($rcode, @ans, @auth, @add);
  
	  if ($qtype eq "A") {
		my ($ttl, $rdata) = (3600, "10.1.2.3");
		push @ans, Net::DNS::RR->new("$qname $ttl $qclass $qtype $rdata");
		$rcode = "NOERROR";
	  }
	  else {
		$rcode = "NXDOMAIN";
	  }
		
	  return ($rcode, \@ans, \@auth, \@add);
  }

  my $ns = Net::DNS::Nameserver->new(
	  LocalPort	   => 5353,
	  ReplyHandler => \&reply_handler,
	  Verbose	   => 1
  );
  
  if ($ns) {
	  $ns->main_loop;
  }
  else {
	  die "couldn't create nameserver object\n";
  }

=head1 BUGS

Net::DNS::Nameserver objects can handle only one query at a time.

=head1 COPYRIGHT

Copyright (c) 2000-2002 Michael Fuhr.  All rights reserved.	This program
is free software; you can redistribute it and/or modify it under
the same terms as Perl itself.

=head1 SEE ALSO

L<perl(1)>, L<Net::DNS>, L<Net::DNS::Resolver>, L<Net::DNS::Packet>,
L<Net::DNS::Update>, L<Net::DNS::Header>, L<Net::DNS::Question>,
L<Net::DNS::RR>, RFC 1035

=cut
