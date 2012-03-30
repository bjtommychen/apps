#!/usr/bin/perl   
use Cwd;

########### CONFIG PARAMETERS###############
my $p_zsim       = $ARGV[0];
my $p_outfile    = $ARGV[1];
my @logfilearray = ( "log1.txt", "log2.txt", "log3.txt", "log4.txt", "log5.txt", "log6.txt", "log7.txt", "log8.txt" );

#work dir
my $inpath     = "input";
my $outpath    = "output";
my $filefilter = "*";

#config
my $recursive = 1;    # do file search recursively or not.
my $maxthread = 1;    # only support quad-cpu-core now.   max is 8.
my $overwrite = 1;    # overwrite output file or not

#control
my $mydebug = 0;      # 1: if just print the commands.

#######################################
my $currdir = getcwd();
my @tarray = ( 0, 0, 0, 0, 0, 0, 0, 0 );

my $i = 0;
my $cmd;

#time
my @filelists;

my $ntotal = 0;
my $ncurr  = 0;

########### Start #############
if ( $ARGV[0] eq "" ) {
	print "mk_cmdlist v1.0 -- by Tommy Chen \n";
	print "Usage: perl mk_cmdlist.pl <inputdir> <outputdir> <file_filter>\n";
	print "Default: Input dir is $inpath/, Output dir is $outpath/. File filter is $filefilter. \n";
	print "Note: file filter is only the .ext name.\n";
	exit(0);
}

if ( $ARGV[0] ne "" ) {
	$inpath = $ARGV[0];
}

if ( $ARGV[1] ne "" ) {
	$outpath = $ARGV[1];
}

if ( $ARGV[2] ne "" ) {
	$filefilter = $ARGV[2];
}

print "Input Dir :", $inpath, "\n", "Output Dir:", $outpath, "\n";

#die "\n";

########### Remove log files ################
foreach $file (@logfilearray) {
	unlink($file);
}

########### GetCurrPath and recursively #############
if (1)    #($recursive == 1)
{
	DoDir($inpath);
}
else {
	opendir DIR, $inpath;
	@filelists = readdir DIR;
	@files     = grep { !-d "$path$_" } @filelists;    #过滤掉目录，只剩文件
	                                                   #my $files = grep{-T "$path$_"} @files; #text files only
}

########### GetCurrPath #############
my $path  = $inpath;
my @files = sort @filelists;                           #

$ntotal = scalar(@files);
print "\nGot filelist ! Total $ntotal files !\n";
for ( $i = 2 ; $i > 0 ; $i-- ) {

	#	print "Start in $i second .... \n";
	#	sleep(1);
}
print "\n";

########### MainLoop #############
foreach $infile (@files) {
	next unless $infile =~ /\.wma$|\.mp3$|\.asf$|\.$filefilter/i;

	#    next unless $infile =~/\.mp3$/i;
	#    print $infile,"\n";

	my $outfile = $infile;
	my $t;
	my $logfile;

	#	$outfile =~s/wma/wav/;
	$outfile =~ s/....$/.out/;
	$outfile = $outpath . $outfile;

	# skip exist file
	if ( $overwrite == 0 ) {
		if ( -e ($outfile) ) {

			#exist
			print "$outfile SKIPPED !\n";
			next unless (0);
		}
		else {

			#not exist
			#print  "find \n";
		}
	}

	# $i is the empty slot.
	$logfile = @logfilearray[$i];

	my $cmd_arg = '-i "' . $path . $infile . '" -o "' . $outfile . '" ' . "";

	{
		$cmd = "run_cmd" . " p1 " . $cmd_arg . "p2";
	}

	print $cmd, "\n";    # $cmd is the New Task !!!

}

############# END OF MAIN ###############

########## Sub Func ###############
sub mysub {
	my @args = @_;
	my $mycmd;

	$mycmd = join( ' ', @args );    #tommy: no use ???

	if ( $mydebug == 0 ) {
		system($cmd);

		# do cmd here !
	}
	else {
		print "$cmd \n";
	}

	return;
}

# 下面的函数将遍历指定目录，
sub DoDir {
	my ($dir) = shift;
	my ($file);

	opendir( DIR, $dir ) || die "Unabel open $dir:$!";
	my (@lfiles) = grep { !/^\.\.?$/ } readdir(DIR);

	#	my @pushfilelist  = grep( s/^/$dir/, @lfiles);
	#	push (@filelists, @lfiles);
	foreach $lfile (@lfiles) {
		my ($rdir) = $dir;
		my $tempdir = $inpath;

		$tempdir =~ s/\\/\\\\/g;

		#handle dir \\dir\file.
		$rdir =~ s/$tempdir//;

		#remove $inpath, get relative path to $inpath.
		my $pathfile = $rdir . '/' . $lfile;
		push( @filelists, $pathfile );
	}

	closedir(DIR);
	foreach (@lfiles) {
		if ( -d ( $file = "$dir/$_" ) )    #check if Directory
		{

			#print "Found a directory:$file\n";

			my $dir2make = $file;
			my $intemp   = $inpath;
			my $outtemp  = $outpath;

			$intemp   =~ s/\\/\\\\/g;
			$outtemp  =~ s/\\/\\\\/g;
			$dir2make =~ s/$intemp/$outtemp/;
			mkdir( $dir2make, 0777 );
			print $dir2make, "\n";
			if ( $recursive == 1 ) {
				DoDir($file);
			}
		}
		else {

			#print "File $file\n";
		}

	}
}
