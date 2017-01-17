use Device::SerialPort;
my $port = Device::SerialPort->new("/dev/ttyACM0");
 
# 19200, 81N on the USB ftdi driver
$port->baudrate(9600); # you may change this value
$port->databits(8); # but not this and the two following
$port->parity("none");
#$port->stopbits(1);
print "Writing\n";
$port-write('1');
$port-write('1');
print "Receiving\n";
while (1) { # and all the rest of the gremlins as they come in one piece
  my $byte = $port->lookfor(); # get the next one
  if ($byte ne "") {  print("got data $byte"); }
  $data .= $byte;
  if (length($data) == 2) { 
    print "Recieved:". unpack('S',$data)."\n";
  }
  #last if $c eq ""; # or we're done
  # print $c; # uncomment if you want to see the gremlin
}
