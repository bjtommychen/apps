use Mail::SendEasy ;
use   Cwd;   
use Sys::Hostname;

################################################
  my  $host = hostname;
  my   $currdir   =   getcwd();    
#control
my $mydebug = 0;	# 1: if just print the commands.


# SMTP config
  my $mail = new Mail::SendEasy(
  smtp => '10.10.0.15' ,
  user => 'BEJBRS@verisilicon.com',
  pass => Vs123456 ,
  ) ;
 
# MAIL body 
my $body;
	$body = $body."<b>Mail Send Easy version 2.0...</b>\n";
   	$body = $body."<p>Send Mail from <font size=+1>$host</font> under <i> $currdir</i> </p>\n";
	$body = $body."<b>End</b>\n"; 

# SEND to	
my @mailto = ('tommy.chen@verisilicon.com','tchen1973@gmail.com'); # the recipient list

	print "Mail Send Easy version 2.0-- by Tommy Chen \n";
	print "Usage: perl MailSendEasy.pl file1 file2 file3 ... \n";
	print "\n";


foreach my $afname(@ARGV){
	my $extname;
	$extname = lc(substr($afname, length($afname)-3,3));

	if ($mydebug == 1)
	{
		print "check attach file $afname \n";
		print "ext name is $extname \n";
	#	if (lc($ARGV[0]) eq 'exe') 
	}
	if ($extname eq 'txt')
	{
		$body = $body."<hr width=90% size=2>\n"; 
		$body = $body."<p>File: <b>$afname</b></p>\n";
		$body = $body."\n";
		
		open(MYINPUTFILE, "<"."$afname");
		my(@lines) = <MYINPUTFILE>;    
		foreach my $line (@lines) 
		{ 
		#	print "$line";
			$body = $body."$line<br>";
			$body = $body."\n";
		}
	}

}

if ($mydebug == 1)
{
	print "Body is :\n $body \n";
	exit;
}	

	
	
foreach my $mailto (@mailto) {
  my $status = $mail->send(
  from    => 'BEJBRS@verisilicon.com' ,
  from_title => 'Tommy Chen' ,
  to      => $mailto,
  subject => "AutoSend Mail" ,
  msg     => "The Plain Msg..." ,
  html    => $body, 
  anex    => [@ARGV],
#  zipanex => [@ARGV],

  ) ;
  print "Send out mail to $mailto done !\n";
 
}  
  if (!$status) { print $mail->error ;}