use Gearman::Worker;  
use Cwd;   
use Switch; 
use Time::Progress;
use threads ('yield', 'stack_size' => 64*4096, 'exit' => 'threads_only', 'stringify');

my $currdir   =   getcwd();   
my $worker; # = Gearman::Worker->new;  
my $mysrv = 'bejlinux:4730';
my $hostoutput;
my $out;
my $maxthread = 2;		# only support quad-cpu-core now. max is 8.
my @tarray = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
my $i = 0;
my $cmd;
my @workers = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);


print "Gearman_worker v1.0 -- by Tommy Chen \n";
print "Usage: perl Gearman_worker.pl <cpucore> \n";

if ($ARGV[0] ne "")
{
  $maxthread = $ARGV[0];
  print "CPU is $maxthread core. \n";
}
print "Register $maxthread worker to '$mysrv' !\n";

for( $i=0; $i< $maxthread; $i=$i+1)
{
  print "Creat $i task \n";
  $worker = 0;
  $worker = Gearman::Worker->new; 
  @workers[$i] = $worker;
  $worker->job_servers($mysrv);  
  $worker->register_function("func",  \&func_docmd);  
	$t = threads->create('mysub', $i); 
	@tarray[$i] = $t;  
  #print "Creat $t task done\n";
}

print "main loop";

while(1)
{
	sleep(1);
  #print ".";
}


#worker function  
########## Sub Func ###############
sub mysub{
  my @args = @_;
  #my $worker;
    
	print "\t\tThread @args[0] Created ! \n";
  #$worker = @workers[@args[0]];
  @workers[@args[0]]->work while 1;  		
	return;
}  
  
#functions  
sub func_docmd {  
  my $time;
  my($job) = @_;
	$subcmd = $_[0]->arg;
  $time = localtime;
   print join(' ', "\n***", $_[0]->handle, ,'Start!', $time, "\n");  
   print join(' ', '***', 'Command: <', $_[0]->arg, '>', "\n");  

    $job->set_status(50, 100);
    
   $out = `$subcmd`;

  $time = localtime;
   print join(' ', '***', $_[0]->handle, ,'Finished!', $time, "\n\n");  

   return  $out;

}   