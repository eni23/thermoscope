try {
  var serialjs = require('serialport-js').node();
  var events   = require('events');
  var is_nwsj = true;
} catch(e) {
  console.log("WARNING: not an nwjs enviroment");
  var is_nwsj = false;
}

var channel_length = 120;
var bar_initialized = false;
var total_ticks = 0;


if (is_nwsj){

  serialjs.find( serial_find_done );
  function serial_find_done( ports ) {
    if( !ports[0] ){
      return;
    }
    serialjs.open(
      ports[0].port,
      serial_start,
      '\n'
    );
  }

  function serial_start( port ){
    port.on('data', serial_rcv_data );
  }

  function serial_rcv_data( data ){
    var aa = data.split("=");
    var id = parseInt(aa[0]);
    var temp = parseFloat(aa[1]);
    var tempf = temp.toFixed(2).substring(0,7);
    total_ticks++;
    if (id>0 && id < 5){
      $("#temp-val-"+id).html(tempf);
      add_temp_data(id, temp);
      $("#tticks").html(total_ticks);
    }
  }

}


$(document).ready(function(){
  $("div.close-app").click(function(){
    window.close();
  });
})


function init_bars(){
  bar_initialized=true;
  for (i=0;i<channel_length;i++){
    $("#bar-area").append("<div class='bar'><div class='bar-fill'></div></div>");
  }
}

function update_bar(num, pct){
  var elem = $("div.bar > div").get(num);
  var rpct = 100 - pct;
  $(elem).css("height",rpct+"%");
}
