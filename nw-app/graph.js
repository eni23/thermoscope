// set up our data series with 50 random data points
var ts = Math.floor(Date.now() / 1000);
var nn = {x:ts,y:22}
var temp_data = [ [nn], [nn], [nn], [nn] ];

var add_temp_data = function(sensor_id, data){
  var ts = Math.floor(Date.now() / 1000);
  var d = { x: ts, y: data };
  temp_data[sensor_id-1].push(d);
}


// instantiate our graph!
var palette = new Rickshaw.Color.Palette( { scheme: 'munin' } );

var graph = new Rickshaw.Graph( {
  element: document.getElementById("chart"),
  width: 835,
  height: 505,
  min:0,
  max:60,
  interpolation:"basis",
  renderer: 'line',
  series: [
    {
      color: palette.color(),
      data: temp_data[3],
      name: 'Sensor 4'
    }, {
      color: palette.color(),
      data: temp_data[2],
      name: 'Sensor 3'
    }, {
      color: palette.color(),
      data: temp_data[1],
      name: 'Sensor 2'
    }, {
      color:  palette.color(),
      data: temp_data[0],
      name: 'Sensor 1'
    }
  ]
} );

graph.render();

var hoverDetail = new Rickshaw.Graph.HoverDetail( {
  graph: graph
} );

var legend = new Rickshaw.Graph.Legend( {
  graph: graph,
  element: document.getElementById('legend')

});
var smoother = new Rickshaw.Graph.Smoother( {
	graph: graph,
	element: document.getElementById('smoother')
} );


var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
  graph: graph,
  legend: legend
} );
var slider = new Rickshaw.Graph.RangeSlider({
  graph: graph,
  element: document.getElementById('slider')
});
var xAxis = new Rickshaw.Graph.Axis.Time( {
	graph: graph,
	timeFixture: new Rickshaw.Fixtures.Time.Local()
} );

xAxis.render();

var yAxis = new Rickshaw.Graph.Axis.Y( {
	graph: graph,
	tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
} );

yAxis.render();


setInterval( function() {
  graph.update();
  slider.update();
}, 250 );


var cci=1;
$("#legend > ul > li > div.swatch").each(function(){
  var col = $(this).css("background-color");
  $(".senscard"+cci+" div.sensident").css("background-color", col);
  cci++;
});

var update_graph_legend = function(){
  var is_single=false;
  var num_active=0;
  var i = 0;
  $("div.tc").removeClass("disabled");
  $("#legend > ul > li").each(function(){
    if ($(this).hasClass("disabled")){
      $("div.tc:eq("+(i)+")").addClass("disabled");
    }
    i++;
  });
}

$("div.tc").click(function(){
  var id = parseInt($(this).attr("sens"));
  var elem = $("#legend span.label:eq("+(id-1)+")");
  elem.trigger("click");
  update_graph_legend();
  return false;
});

$("div.co").click(function(){
  var id = parseInt($(this).parent().attr("sens"));
  var elem = $("#legend a.action:eq("+(id-1)+")");
  elem.trigger("click");
  update_graph_legend();
  return false;
});



$( "#slider-minmax" ).slider({
			range: true,
			min: -25,
			max: 180,
			values: [ 0, 60 ],
			slide: function( event, ui ) {
				$("#range-min").html(ui.values[ 0 ])
        $("#range-max").html(ui.values[ 1 ])
        graph.configure({
          min:ui.values[ 0 ],
          max:ui.values[ 1 ]
        });
        graph.update();


			}
		});
