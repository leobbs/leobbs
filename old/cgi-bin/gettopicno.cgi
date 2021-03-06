#!/usr/bin/perl
#####################################################
#  LEO SuperCool BBS / LeoBBS X / 雷傲极酷超级论坛  #
#####################################################
# 基于山鹰(糊)、花无缺制作的 LB5000 XP 2.30 免费版  #
#   新版程序制作 & 版权所有: 雷傲科技 (C)(R)2004    #
#####################################################
#      主页地址： http://www.leobbs.org/            #
#      论坛地址： http://bbs.leobbs.org/            #
#####################################################

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

use warnings;
use strict;
use diagnostics;

use LBCGI;
$LBCGI::POST_MAX = 200000;
$LBCGI::DISABLE_UPLOADS = 1;
$LBCGI::HEADERS_ONCE = 1;
require "code.cgi";
require "data/boardinfo.cgi";
require "data/styles.cgi";
require "bbs.lib.pl";
$|++;

$thisprog = "gettopicno.cgi";

$query = new LBCGI;
$in_forum = $query->param('forum');
$in_topic = $query->param('topic');
&error("打开文件&老大，别乱黑我的程序呀！") if (($in_topic !~ /^[0-9]+$/) || ($in_forum !~ /^[0-9]+$/));
$inshow = $query->param('show');
$inact = $query->param('act');
&error("打开文件&老大，别乱黑我的程序呀！") if (($inact !~ "pre") && ($inact !~ "next"));

open(FILE, "${lbdir}boarddata/listno$in_forum.cgi");
sysread(FILE, $listall, (stat(FILE))[7]);
close(FILE);
$listall =~ s/\r//isg;

if ($inact eq "pre") {
    if ($listall =~ m/^$in_topic\n/) {&error("普通错误&这已经是第一个帖子了！");}
    else {
        $listall =~ m/.*(^|\n)(.+?)\n$in_topic\n/;
        $in_topic = $2;
    }
}
else {
    if ($listall =~ m/(^|\n)$in_topic\n$/) {&error("普通错误&这已经是最后一个帖子了！");}
    else {
        $listall =~ m/.*(^|\n)$in_topic\n(.+?)\n/;
        $in_topic = $2;
    }
}
print header(-charset => "UTF-8", -expires => "$EXP_MODE", -cache => "$CACHE_MODES");
print "<script language='javascript'>document.location = 'topic.cgi?forum=$in_forum&topic=$in_topic&show=$inshow'</script>";
exit;
