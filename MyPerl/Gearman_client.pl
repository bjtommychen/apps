#!/usr/bin/perl   
use Cwd;   
use Switch; 
use Time::Progress;
use threads ('yield', 'stack_size' => 64*4096, 'exit' => 'threads_only', 'stringify');
use Gearman::Client;  


########### CONFIG PARAMETERS###############
my $p_zsim = $ARGV[0];
my $p_outfile = $ARGV[1]; 
my @logfilearray = ( "log1.txt", "log2.txt", "log3.txt" , "log4.txt", "log5.txt", "log6.txt", "log7.txt" , "log8.txt" );

#work dir
my $inpath="input";
#my $inpath ="\\\\bejlinux\\wma9_test_streams\\input";
my $outpath="output";

#config
my $recursive = 1; 		# do file search recursively or not.
my $maxthread = 8;		# only support quad-cpu-core now.   max is 8.
my $overwrite = 1;  	# overwrite output file or not
#control
my $mydebug = 0;	# 1: if just print the commands.

#######################################
my   $currdir   =   getcwd();   
my @tarray = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);

my $i = 0;
my $cmd;

my @clients = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0); 
my $client; 
my $mysrv = 'bejlinux:4730';

#time
my $pasttime = new Time::Progress;
my @filelists ;

my $ntotal = 0;
my $ncurr = 0;
$pasttime->restart;
my $maxlen = 0;
  
  
########### Start #############
print "Gearman_clients v1.0 -- by Tommy Chen \n";

if (1) #($ARGV[0] eq "")
{
	#print "Gearman_clients (support multi-cpu-core) v0.4 -- by Tommy Chen \n";
	print "Usage: perl Gearman_clients.pl <exe> <wmadec.exe> \n";
	print "Usage: perl Gearman_clients.pl <zisimg2> <wmadec.out> \n";
	print "Default: Input dir is $inpath/, Output dir is $outpath/, MaxThread is $maxthread cpu(s). \n";
   
	print "Default: Recursive is $recursive. OverWrite is $overwrite \n";
 
	print "\n";

}
if ($ARGV[0] eq "")
{
	die "\n";	
}

########### Remove log files ################
foreach $file (@logfilearray)
{
	unlink ($file);
}


########### GEARMAN ################
for( $i=0; $i< $maxthread; $i=$i+1)
{
  #print "Creat $i task \n";
  $client = 0;
  $client = Gearman::Client->new;  
  @clients[$i] = $client;
  $client->job_servers($mysrv);  
  print "Creat $i task done\n";
}



########### GetCurrPath and recursively ############# 
if (1)#($recursive == 1)
{
	DoDir($inpath);
}
else
{
	opendir DIR, $inpath;
	@filelists = readdir DIR;
	@files = grep{!-d "$path$_"} @filelists; #过滤掉目录，只剩文件
	#my $files = grep{-T "$path$_"} @files; #text files only
}


########### GetCurrPath #############
my $path = $inpath;
my @files = @filelists; # 

$ntotal  = 
 scalar(@files) ;
print "\nGot filelist ! Total $ntotal files !\n";
for($i = 5; $i>0; $i--)
{ 
	print "Start in $i second .... \n";
	#sleep(1);
} 
print "\n";

########### MainLoop #############
foreach $infile (@files)
{
    next unless $infile =~/\.wma$|\.mp3$|\.asf$|\.god$/i;
#    next unless $infile =~/\.mp3$/i;
#    print $infile,"\n";

	my $outfile =$infile;
	my $t;
	my $logfile;
		
#	$outfile =~s/wma/wav/;
	$outfile =~s/....$/.wav/;
	$outfile = $outpath.$outfile;

		# skip exist file 
		if ($overwrite == 0)
		{   
			if (-e ($outfile)) 
			{ 
				#exist
				print "$outfile SKIPPED !\n";
	 			next unless (0);	 
			}
	 		else 
	 		{   
	 			#not exist
	 			#print  "find \n";
	 		}
		}	 
	
 
	while(1)
	{		
		
		for( $i=0; $i< $maxthread; $i=$i+1)
		{
			$t = @tarray[$i];
			if ($t !=0 && $t->is_running())
			{
				#sleep 1;	
			}
			else
			{
				if($t)
				{
				    if ($t->is_joinable()) 
				    {
				        $t->join(); 
				    } 
				}

				@tarray[$i] = 0;
   	 			#print $pasttime->report( "done %p elapsed: %L (%l sec), ETA %E (%e sec)\n", 50 );
				last if (1);
			}
		}
 
		last if ($i<$maxthread);
		
		sleep 1;
	}	
		
	$logfile 
= @logfilearray[$i];
	
	my $cmd_arg = '"'.$path.$infile.'"  "'.$outfile.'"   >>'.$logfile;

	if (lc($ARGV[0]) eq 'exe') 
	{
		$cmd = $ARGV[1]." ".$cmd_arg;
	}
	else
	{
		$cmd = $ARGV[0].' '.$ARGV[1]." -q -ignore -exec -cl ".$cmd_arg;
	}

#	print $cmd,"\n";
	$t = threads->create('mysub', $i); #$cmd); 
	@tarray[$i] = $t;
	
	$ncurr ++;
	if($ncurr % 10 == 0)
	{
		print "[$ncurr/$ntotal] ".$pasttime->report("Done %p, Elapsed: %L \n", $ncurr*100/$ntotal);
	}
    print('Thread ', $i, ': ', $path.$infile, "\n");

}
 
########### MainLoop end#############

	# wait all finished.
	{		
		for( $i=0; $i< $maxthread; $i=$i+1)
		{
			$t = @tarray[$i];
			while ($t !=0 && $t->is_running())
			{
				sleep 1;	
			}

			@tarray[$i] = 0;
		}
 
	}	

  print $pasttime->report( "done %p elapsed: %L (%l sec), ETA %E (%e sec)\n", 100 );



########### Post Msg #############
if (0)#($mydebug == 0)
{ 
	my $logfiles ;
	
	unlink ("myziped.zip");
	open (LOGFILE, ">log.txt");
	for( $i=0; $i< $maxthread; $i=$i+1)
 
 
	{
#	 $logfiles = $logfiles." ".@logfilearray[$i]; 
	  	open (ONELOGFILE, "< @logfilearray[$i] ");
	   	while(<ONELOGFILE>)
	    {
	     	print LOGFILE $_;
	    }
	}
	#system ("perl zlib_add.pl log.txt");
	#system ("perl MailSendEasy.pl myziped.zip");
}


########## Sub Func ###############
sub mysub{
    my @args = @_;
    my $mycmd;
    my $result;
    
    $mycmd = join(' ', @args);
		#print "do cmd:$cmd \n";

		if ($mydebug == 0)
		{
			$result = @clients[@args[0]]->do_task("func", $cmd);
		}
		print $$result;		

	return;
}

# 下面的函数将遍历指定目录，
sub DoDir{
	my($dir) = shift;
	my($file);
  my $len;

	opendir(DIR, $dir) || die "Unabel open $dir:$!";
	my(@lfiles) = grep {!/^\.\.?$/ } readdir(DIR);
 
 
#	my @pushfilelist  = grep( s/^/$dir/, @lfiles);
#	push (@filelists, @lfiles);
	foreach $lfile (@lfiles)
	{	
		my($rdir) = $dir;
		my $tempdir = $inpath;
		

		$tempdir =~s/\\/\\\\/g;
 	 	#handle dir \\dir\file.
		$rdir =~s/$tempdir//;
 	 	#remove $inpath, get relative path to $inpath. 
		my $pathfile = $rdir.'/'.$lfile;

		#get file size.
		$len = -s "$dir/$lfile";
		#print "$dir/$lfile size is $len \n";		
		
		if ($len >$maxlen)
		{
   		print "$dir/$lfile size is $len \n";		
			unshift (@filelists, $pathfile);
			$maxlen = $len;
		}
		else{
			push (@filelists, $pathfile);
			
		}

	}

	closedir(DIR);
	foreach (@lfiles) 
	{
		if(-d($file="$dir/$_"))	 #check if Directory
		{
			#print "Found a directory:$file\n";
 
 
 
			my $dir2make  = $file;
			my $intemp = $inpath;
			my $outtemp = $outpath;
			
			$intemp =~s/\\/\\\\/g;
			$outtemp =~s/\\/\\\\/g;
			$dir2make =~s/$intemp/$outtemp/; 
			mkdir ($dir2make, 0777);
			print  $dir2make, "\n";
			if ($recursive == 1)
			{
			DoDir($file);
			}
		}
		else
		{ 
			#print "File $file\n";	
	
		}
 
	}
}