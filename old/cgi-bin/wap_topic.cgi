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
require "data/styles.cgi";
require "wap_code.cgi";
require "wap.pl";
$|++;
&waptitle;
$show .= qq~<card  title="$board_name"> ~;
$lid = $query->param('lid');
&check($lid);
$pa = $query->param('pa');
if ($in_member_name eq "" || $in_member_name eq "客人") {
    $in_member_name = "客人";
}
else {
    &getmember("$in_member_name", "no");
}
$in_forum = $query->param('f');
$in_topic = $query->param('t');
&getoneforum("$in_forum");
$myinmembmod = $inmembmod;
&errorout("打开主题&这个主题不存在！可能已经被删除！") unless (-e "${lbdir}forum${inforum}/${intopic}.thd.cgi");
my $filetoopen = "${lbdir}forum$in_forum/$in_topic.pl";
&winlock($filetoopen) if ($OS_USED eq "Nt");
open(FILE, "$filetoopen");
flock(FILE, 2) if ($OS_USED eq "Unix");
my $topicinfo = <FILE>;
close(FILE);
chomp $topicinfo;
$topicinfo =~ s/[\a\f\n\e\0\r]//isg;
($topicid, $topictitle, $topicdescription, $threadstate, $threadposts, $threadviews, $startedby, $startedpostdate, $lastposter, $lastpostdate, $posticon, $inposttemp, $addmetype) = split(/\t/, $topicinfo);
if (($topictitle eq "") || ($startedby eq "") || ($startedpostdate eq "") || ($threadposts eq "") || ($threadposts > 1000000)) {
    require "dorepiretopic.pl";
}
else {
    $posticon =~ s/\s//isg;
    if ($posticon =~ /<br>/i) {$posticon = "<br>";}
    $threadviews = ($threadposts + 1) * 8 if ($threadviews eq "");
}
$threadviews++;

if ($topictitle ne "") {
    open(FILE, ">$filetoopen");
    flock(FILE, 2) if ($OS_USED eq "Unix");
    print FILE "$topicid\t$topictitle\t$topicdescription\t$threadstate\t$threadposts\t$threadviews\t$startedby\t$startedpostdate\t$lastposter\t$lastpostdate\t$posticon\t$inposttemp\t$addmetype\t";
    close(FILE);
}
&winunlock($filetoopen) if ($OS_USED eq "Nt");
$mymembercode = $member_code;
$myinmembmod = $inmembmod;
$myrating = $rating;
$tempaccess = "forumsallowed" . $in_forum;
$test_entry = $query->cookie($tempaccess);
$allowed = $allowed_entry{$in_forum} eq "yes" || ($test_entry eq $forum_pass && $test_entry ne "") || $mymembercode eq "ad" || $mymembercode eq "smo" || $myinmembmod eq "yes" ? "yes" : "no";

&errorout("打开文件&老大，别乱黑我的程序呀！") if ($in_forum !~ /^[0-9]+$/);
&errorout("打开文件&老大，别乱黑我的程序呀！") if ($in_topic !~ /^[0-9]+$/);
&getoneforum($in_forum);
if (-e "${lbdir}data/style${inforum}.cgi") {require "${lbdir}data/style${inforum}.cgi";}
&errorout("进入论坛&你的论坛组没有权限进入论坛！") if ($yxz ne '' && $yxz !~ /,$member_code,/);
$addtimes = ($timedifferencevalue + $timezone) * 3600;
&errorout("进入会员论坛查看帖子内容&您是客人没有权限进入!") if ($in_member_name eq "客人" && $reg_access eq "on" && &checksearchbot);
&errorout("进入私有论坛&对不起，您没有权限进入该私有论坛！") if ($privateforum eq "yes" && $allowed ne "yes");
if (($startnewthreads eq "cert") && (($member_code ne "ad" && $member_code ne "smo" && $member_code ne "cmo" && $member_code ne "mo" && $member_code ne "amo" && $member_code !~ /^rz/) || ($in_member_name eq "客人")) && ($userincert eq "no")) {&errorout("进入论坛&你一般会员不允许进入此论坛！");}

if ($allow_users ne '') {
    &errorout('进入论坛&你不允许进入该论坛！') if (",$allow_users," !~ /,$in_member_name,/i && $member_code ne 'ad');
}

if ($member_code ne 'ad' && $member_code ne 'smo' && $inmembmod ne 'yes') {
    &errorout("进入论坛&你不允许进入该论坛，你的威望为 $rating，而本论坛只有威望大于等于 $enterminweiwang 的才能进入！") if ($enterminweiwang > 0 && $rating < $enterminweiwang);
    if ($enterminmony > 0 || $enterminjf > 0) {
        require "data/cityinfo.cgi" if ($addmoney eq "" || $replymoney eq "" || $moneyname eq "");
        $mymoney1 = $numberofposts * $addmoney + $numberofreplys * $replymoney + $visitno * $loginmoney + $mymoney - $postdel * $delmoney + $jhcount * $addjhhb;
        &errorout("进入论坛&你不允许进入该论坛，你的金钱为 $mymoney1，而本论坛只有金钱大于等于 $enterminmony 的才能进入！") if ($enterminmony > 0 && $mymoney1 < $enterminmony);
        &errorout("进入论坛&你不允许进入该论坛，你的积分为 $jifen，而本论坛只有积分大于等于 $enterminjf 的才能进入！") if ($enterminjf > 0 && $jifen < $enterminjf);
    }
}
$topictitle =~ s/^＊＃！＆＊//;
my $filetoopen = "$lbdir" . "forum$in_forum/$in_topic.thd.cgi";
open(FILE, "$filetoopen");
my @threads = <FILE>;
close(FILE);
$rn = 1;
my $a;
if ($mymembercode eq "ad" || $mymembercode eq "smo" || $myinmembmod eq "yes") {
    $viewhide = 1;
}
else {
    $viewhide = 0;
    if ($hidejf eq "yes") {
        my @viewhide = grep (/^$in_member_name\t/i, @threads);
        $viewhide = @viewhide;
        $viewhide = 1 if ($viewhide > 1);
    }
}
$StartCheck = $numberofposts + $numberofreplys;
$member_code = "no";
$paGe = $query->param('paGe');
my $all_1 = @threads / $topicpre;
if ($all_1 > int($all_1)) {$all_1 = int($all_1) + 1;}
$paGe = ($paGe eq '' || $paGe <= 0) ? "1" : "$paGe";
my $k = ($paGe - 1) * $topicpre;
if ($k > @threads) {$k = 0;}
my $s = $k + $topicpre;
for ($ij = $paGe - 2; $ij <= $paGe + 3; $ij++) {
    next if ($ij < 1);
    next if ($ij > $all_1);
    if ($ij ne $paGe) {$newpage .= "&nbsp;<a href=\"wap_topic.cgi?t=$in_topic&amp;paGe=$ij&amp;f=$in_forum&amp;lid=$lid&amp;pa=$pa\">$ij</a>";}
    else {$newpage .= "&nbsp;<i>$ij</i>";}
}
$newpage or $newpage = ' <i>1</i>';
for ($i = $k; $i < $s; $i++) {
    next if ($threads[$i] eq '');
    $rn = $i + 1;
    ($membername, my $topictitle, $no, $no, $no, my $postdate, my $post) = split(/\t/, $threads[$i]);
    &lbcode(\$post);
    my $postsize = length($post);
    if ($postsize > $mastnum) {
        $post =~ s/<br>/\n/g;
        $post =~ s/<p>/\\n\\n/g;
        $post =~ s/<(.*?)>//g;
        $post = substr($post, 0, $mastnum);
        if ($post =~ /^([\000-\177]|[\241-\371][\75-\376])*([\000-\177]|[\241-\377][\75-\376])$/) {}
        else {chop($post);}
        $post =~ s/\\n/<br\/>/g;
        $post =~ s/\&/\&amp;/isg;
        $post =~ s/\&amp;nbsp;/\&nbsp;/g;
        $post =~ s/\&amp;gt;/\&gt;/g;
        $post =~ s/\&amp;lt;/\&lt;/g;
        $post =~ s/\&amp;#36;/\＄/g;
        $post =~ s/\&amp\;(.{1,6})\&\#59\;/\&$1\;/isg;
        $post =~ s/\&\#([0-9]{1,6})\&\#59\;/\&\#$1\;/isg;
        $post =~ s/\&amp;quot;/\"/g;
        $post =~ s/\&amp;#59;/\;/g;
        $post =~ s/\&amp;#35;/\&#35;/g;
        $post =~ s/\&amp;amp;/\&amp;/g;
        chomp $post;
        $post .= "<a href=\"wap_topic_all.cgi?f=$in_forum&amp;lid=$lid&amp;t=$in_topic&amp;pno=$i&amp;pa=$pa\">&gt;&gt;</a>";
    }
    else {
        $post =~ s/<br>/<br\/>/g;
        $post =~ s/<p>/<br\/><br\/>/g;
        $post =~ s/\&amp;nbsp;/\&nbsp;/g;
    }
    $postdate = &dateformat($postdate + ($timedifferencevalue * 3600) + ($timezone * 3600));
    $a .= qq~<p>$rn楼：$postdate<br/>作者:$membername<br/>$post($postsize字)<br/>------------</p>~;
}
my $r = &msg($in_member_name);
$show .= qq~<p>$r<b>标题：$topictitle</b><br/><small>($threadviews,$#threads,$startedby)</small><br/>----------</p>$a<p>[$paGe/$all_1页]</p><p>$newpage</p><p>跳到<input type="text" name="tz" size="5" maxlength="5" format="*N"/><a href="wap_topic.cgi?t=$in_topic&amp;paGe=\$(tz)&amp;f=$in_forum&amp;lid=$lid&amp;paGe=$pa">Go..</a></p><p><a href="wap_forum.cgi?forum=$in_forum&amp;lid=$lid&amp;paGe=$pa">返回$forumname</a><br/><a href="wap_re.cgi?f=$in_forum&amp;lid=$lid&amp;t=$in_topic">回复帖子</a><br/><a href="wap_index.cgi?lid=$lid">论坛首页</a></p>~;
&wapfoot;