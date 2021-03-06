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
$LBCGI::POST_MAX = 500000;
$LBCGI::DISABLE_UPLOADS = 1;
$LBCGI::HEADERS_ONCE = 1;
require "data/boardinfo.cgi";
require "data/styles.cgi";
require "bbs.lib.pl";
$|++;

$thisprog = "report.cgi";

$query = new LBCGI;

&ipbanned; #封杀一些 ip

$in_forum = $query->param('forum');
$in_topic = $query->param('topic');
&error("打开文件&老大，别乱黑我的程序呀！") if (($in_topic) && ($in_topic !~ /^[0-9]+$/));
&error("打开文件&老大，别乱黑我的程序呀！") if (($in_forum) && ($in_forum !~ /^[0-9]+$/));
if (-e "${lbdir}data/style${inforum}.cgi") {require "${lbdir}data/style${inforum}.cgi";}

$action = $query->param('action');

$insubject = $query->param('subject');
$inemailmessage = $query->param('emailmessage');
$emailtopictitle = $query->param('emailtopictitle');
$intouser = $query->param('touser');
$in_member_name = $query->param('membername');
$in_password = $query->param('password');
if ($in_password ne "") {
    eval {$in_password = md5_hex($in_password);};
    if ($@) {eval('use Digest::MD5 qw(md5_hex);$in_password = md5_hex($in_password);');}
    unless ($@) {$in_password = "lEO$in_password";}
}

$inmsgtitle = $query->param('subject');
$inmessage = $query->param('emailmessage');
$inoriginalpost = $query->param('originalpost');
$inpost2 = "<BR><BR><b>贴子原始位置：</b> $boardurl/topic.cgi?forum=$in_forum&topic=$in_topic<br>";

$insubject = &cleaninput($insubject);
$inemailmessage = &cleaninput($inemailmessage);
$emailtopictitle = &cleaninput($emailtopictitle);
$in_forum = &cleaninput($in_forum);
$inoriginalpost = &cleaninput($inoriginalpost);

$in_member_name = &cleaninput($in_member_name);
$in_password = &cleaninput($in_password);
$in_post_no = $query->param('postno');

$inmessage2 = $inemailmessage . $inoriginalpost . $inpost2;

# new
$add_user2 = $query->param('touser1');
# -- new

print header(-charset => "UTF-8", -expires => "$EXP_MODE", -cache => "$CACHE_MODES");

$in_select_style = $query->cookie("selectstyle");
$in_select_style = $skin_selected if ($in_select_style eq "");
&error("普通错误&老大，别乱黑我的程序呀！") if (($in_select_style =~ m/\//) || ($in_select_style =~ m/\\/) || ($in_select_style =~ m/\.\./));
if (($in_select_style ne "") && (-e "${lbdir}data/skin/${inselectstyle}.cgi")) {require "${lbdir}data/skin/${inselectstyle}.cgi";}

if (!$in_member_name) {$in_member_name = cookie("amembernamecookie");}
if (!$in_password) {$in_password = cookie("apasswordcookie");}
$in_member_name =~ s/[\a\f\n\e\0\r\t\`\~\!\@\#\$\%\^\&\*\(\)\+\=\\\{\}\;\'\:\"\,\.\/\<\>\?]//isg;
$in_password =~ s/[\a\f\n\e\0\r\t\|\@\;\#\{\}\$]//isg;

&error("短消息禁止使用&很抱歉，坛主由于某种原因已禁止所有用户使用短消息功能") if ($allowusemsg eq "off");
&error("论坛已经关闭&很抱歉，由于论坛暂时关闭，请稍后再来使用短消息，谢谢合作！") if (($mainoff == 1) || ($mainonoff == 1));
if ($catbackpic ne "") {$catbackpic = "background=$imagesurl/images/$skin/$catbackpic";}

if ($in_member_name eq "" || $in_member_name eq "客人") {
    $in_member_name = "客人";
    $userregistered = "no";
}
else {
    #			&getmember("$in_member_name");
    &getmember("$in_member_name", "no");
    &error("普通错误&此用户根本不存在！") if ($userregistered eq "no");
    if ($in_password ne $password) {&error("发送报告&你的密码有问题！");}
}

&title;

$output .= qq~<BR>
<table width=$tablewidth align=center cellspacing=0 cellpadding=0><tr><td>>>> 在这里您可以把有问题的帖子发送给管理人员处理</td></tr></table>
<table width=$tablewidth align=center cellspacing=0 cellpadding=1 bgcolor=$navborder><tr><td><table width=100% cellspacing=0 cellpadding=3 height=25><tr><td bgcolor=$navbackground><img src=$imagesurl/images/item.gif align=absmiddle width=11> <font face="$font" color=$navfontcolor> <a href="leobbs.cgi">$board_name</a>  → 报告有问题的贴子<td bgcolor=$navbackground align=right></td></tr></table></td></tr></table>
<p>
<SCRIPT>valigntop()</SCRIPT>
<table cellpadding=0 cellspacing=0 width=$tablewidth bgcolor=$tablebordercolor align=center>
    <tr>
        <td>
        <table cellpadding=6 cellspacing=1 width=100%>
        ~;

if ($action eq "send") {

    #	&getmember("$in_member_name");
    if ($userregistered eq "no") {&error("发送报告&你还没注册呢！");}
    elsif ($in_password ne $password) {&error("发送报告&你的密码有问题！");}
    elsif ($in_member_name eq "") {&login("$thisprog?action=reply&touser=$intouser");}

    # Check for blanks

    if ($inmsgtitle eq "") {$blanks = "yes";}
    if ($inmessage eq "") {$blanks = "yes";}
    if ($intouser eq "") {$blanks = "yes";}

    if ($blanks eq "yes") {&error("发送报告&请完整填写表单，不要遗漏！");}

    $memberfilename = $intouser;
    $memberfilename =~ s/ /\_/g;
    $memberfilename =~ tr/A-Z/a-z/;
    $currenttime = time;
    my $messfilename = "${lbdir}${msgdir}/main/${memberfilename}_mian.cgi";
    &error("不允许发送短信息&对方设置了短信息免打扰，无法发送！<br>") if (-e $messfilename);

    #	            &getmember("$memberfilename");
    &getmember("$memberfilename", "no");
    if ($userregistered eq "no") {&error("发送报告&这个版主有问题，请更换一个发送报告！");}

    $filetoopen = "$lbdir" . "$msgdir/in/$memberfilename" . "_msg.cgi";
    open(FILE, "$filetoopen");
    @inboxmessages = <FILE>;
    close(FILE);

    open(FILE, ">$filetoopen");
    flock(FILE, 2) if ($OS_USED eq "Unix");
    print FILE "＊＃！＆＊$in_member_name\tno\t$currenttime\t$inmsgtitle\t$inmessage2\n";
    foreach $line (@inboxmessages) {
        chomp $line;
        print FILE "$line\n";
    }
    close(FILE);

    if ($refreshurl == 1) {
        $relocurl = "topic.cgi?forum=$in_forum&topic=$in_topic";
    }
    else {
        $relocurl = "forums.cgi?forum=$in_forum";
    }

    $output .= qq~
            <tr>
                <td bgcolor=$miscbacktwo align=center><font color=$fontcolormisc><b>谢谢，$in_member_name！已经成功将报告发送给版主了</b></td>
            </tr>

            <tr>
            <td bgcolor=$miscbackone><font color=$fontcolormisc>
            如果浏览器没有自动返回，请点击下面的链接！
            <ul>
            <li><a href="topic.cgi?forum=$in_forum&topic=$in_topic">返回主题</a>
            <li><a href="forums.cgi?forum=$in_forum">返回论坛</a>
            <li><a href="leobbs.cgi">返回论坛首页</a>
            </ul>
            </tr>
            </td>
            </table></td></tr></table><SCRIPT>valignend()</SCRIPT>
            <meta http-equiv="refresh" content="3; url=$relocurl">
            ~;

} # end action

else {

    $filetoopen = "$lbdir" . "forum$in_forum/foruminfo.cgi";
    open(FILE, "$filetoopen");
    $forums = <FILE>;
    close(FILE);
    ($forumid, $category, $categoryplace, $forumname, $forumdescription, $forummoderator, $htmlstate, $idmbcodestate, $privateforum, $startnewthreads, $lastposter, $lastposttime, $threads, $posts, $forumgraphic, $miscad2, $misc, $forum_pass, $hiddenforum, $indexforum, $teamlogo, $teamurl, $fgwidth, $fgheight, $miscad4, $todayforumpost, $miscad5) = split(/\t/, $forums);

    $filetoopen = "$lbdir" . "forum$in_forum/$in_topic.thd.cgi";
    open(FILE, "$filetoopen");
    flock(FILE, 2);
    $threads = <FILE>;
    close(FILE);
    chomp $threads;
    ($membername, $topictitle, $postipaddress, $showemoticons, $showsignature, $postdate, $post, $posticon) = split(/\t/, $threads);
    $topictitle =~ s/^＊＃！＆＊//;

    $post =~ s/\<p\>/\n\n/g;
    $post =~ s/\<br\>/\n/g;

    $postdate = $postdate + ($timedifferencevalue * 3600) + ($timezone * 3600);
    $postdate = &dateformat("$postdate");

    $rawpost = $post;
    $rawpost =~ s/\[USECHGFONTE\]//sg;
    $rawpost =~ s/\[DISABLELBCODE\]//sg;
    $rawpost =~ s/\[ADMINOPE=(.+?)\]//isg;
    $rawpost =~ s/\[ALIPAYE\](.*)\[ALIPAYE\]//isg;

    if ($rawpost =~ /\[POSTISDELETE=(.+?)\]/) {
        if ($1 ne " ") {$presult = "<BR>屏蔽理由：$1<BR>";}
        else {$presult = "<BR>";}
        $rawpost = qq(<br>--------------------------<br><font color=$posternamecolor>此帖子内容已经被单独屏蔽！$presult如有疑问，请联系管理员！</font><br>--------------------------<BR>);
    }

    $temppost = qq~原始贴子由 $membername 在 $postdate 发布，内容如下：\[br\]$rawpost~;


    ### print form
    if ($forummoderator eq "") {
        &error("发送报告&本版块没有设置版主！");}
    else {
        $recipient = $forummoderator}

    @recipientname = split(",", $recipient);

    $toto = qq~<select name="touser">~;
    foreach (@recipientname) {
        $toto .= qq~<option value="$_">$_</option>~;
    }
    $toto .= qq~</select>~;
    &getoneforum("$in_forum");

    &error("发送报告&你就是版主，搞什么飞机？") if (($member_code eq "ad") || ($member_code eq 'smo') || ($inmembmod eq "yes"));

    $topictitle = &cleanarea("$topictitle");

    $output .= qq~
    <form action="$thisprog" method=post>
    <input type=hidden name="action" value="send">
    <input type=hidden name="forum" value="$in_forum">
    <input type=hidden name="topic" value="$in_topic">
    <input type=hidden size=40 name="subject" value="报告有问题的贴子： $topictitle">
	<tr>
    		<td bgcolor=$titlecolor $catbackpic valign=middle colspan=2 align=center>
			<font color=$fontcolormisc><b>向管理员报告有问题的贴子</b></font>
		</td>
	</tr>
<tr><td bgcolor=$miscbacktwo colspan=2><font color=$titlefontcolor>您目前的身份是： <font color=$fonthighlight><B><u>$in_member_name</u></B></font> ，要使用其他用户身份，请输入用户名和密码。未注册客人请输入网名，密码留空。</td></tr>
<tr><td bgcolor=$miscbackone><font color=$fontcolormisc>请输入您的用户名</font></td><td bgcolor=$miscbackone><input type=text name="membername"> &nbsp; <font color=$fontcolormisc><span onclick="javascript:location.href='register.cgi?forum=$in_forum'" style="cursor:hand">您没有注册？</span></td></tr>
<tr><td bgcolor=$miscbackone><font color=$fontcolormisc>请输入您的密码</font></td><td bgcolor=$miscbackone><input type=password name="password"> &nbsp; <font color=$fontcolormisc><a href="profile.cgi?action=lostpass" style="cursor:help">忘记密码？</a></font></td></tr>
	<tr>
                <td bgcolor=$miscbackone valign=middle><font color=$fontcolormisc><b>报告发送给哪个版主</b></font>
		</td>
                <td bgcolor=$miscbackone valign=middle>$toto
		</td>
	</tr>
	<tr>
    		<td bgcolor=$miscbackone>
		<font color=$fontcolormisc><b>报告原因：</b><br>垃圾贴、广告贴、非法贴等。。。<BR>非必要情况下不要使用这项功能！
		</td>
    		<td bgcolor=$miscbackone><textarea name="emailmessage" cols="55" rows="6">
管理员，您好，由于如下原因，我向你报告这有问题的贴子：

</textarea><input type=hidden name="originalpost" value="$temppost"></td>
	</tr>
	<tr>
    		<td colspan=2 bgcolor=$miscbackone align=center><input type=hidden name="emailtopictitle" value="$topictitle"><input type=submit value="发送报告" name="Submit"></table></td></form></tr></table><SCRIPT>valignend()</SCRIPT>
    ~;

} # end routine.

&output($board_name, \$output);
exit;
