#!/usr/bin/perl
#########################
# 手机论坛WAP版
# By Maiweb 
# 2005-11-08
# leobbs-vip.com
#########################
BEGIN {
    $startingtime = (times)[0] + (times)[1];
    foreach ($0, $ENV{'PATH_TRANSLATED'}, $ENV{'SCRIPT_FILENAME'}) {
        my $LBPATH = $_;
        next if ($LBPATH eq '');
        $LBPATH =~ s/\\/\//g;
        $LBPATH =~ s/\/[^\/]+$//o;
        unshift(@INC, $LBPATH);
    }
}
use strict;
use warnings;
use diagnostics;
use diagnostics;

use LBCGI;
$query = new LBCGI;
$LBCGI::POST_MAX = 2000;
$LBCGI::DISABLE_UPLOADS = 1;
$LBCGI::HEADERS_ONCE = 1;
require "data/boardinfo.cgi";
require "wap.lib.pl";
require "wap.pl";
require "data/styles.cgi";
$|++;
&waptitle;
$show .= qq~<card  title="保存短消息">~;
$lid = $query->param('lid');
&check($lid);
$in_topictitle = $query->param('title');
if ($in_member_name eq "" || $in_member_name eq "客人") {
    $in_member_name = "客人";
}
else {
    &getmember("$in_member_name", "no");
}
$name = $query->param('name');
$name = $uref->fromUTF8("UTF-8", $name);
&getmember("$name", "no");
&erroroutout("普通错误&此用户根本不存在！") if ($userregistered eq "no");
$inpost = $query->param('inpost');
$inpost = $uref->fromUTF8("UTF-8", $inpost);
$in_topictitle = $uref->fromUTF8("UTF-8", $in_topictitle);
$inpost = &cleaninput("$inpost");
$in_topictitle = &cleaninput("$in_topictitle");

my $currenttime = time;
my $filetomake = "$lbdir$msgdir/in/$name\_msg.cgi";
if (open(FILE, $filetomake)) {
    @filedata = <FILE>;
    close(FILE);
}
open(FILE, ">$filetomake");
print FILE "$in_member_name\tno\t$currenttime\t$in_topictitle\t$inpost\n";
foreach (@filedata) {
    chomp;
    print FILE "$_\n";
}
close(FILE);
undef @filedata;
$show .= qq~<p>成功发送!<br/><a href="wap_index.cgi?lid=$lid">返回首页</a></p><p><a href="wap_sms.cgi?lid=$lid">返回短消息</a></p>~;
&wapfoot;