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

var graph = new Rickshaw.Graph( {
  element: document.getElementById("chart"),
  width: 835,
  height: 510,
  min:0,
  interpolation:"basis",
  renderer: 'line',
  series: [
    {
      color: "#c05020",
      data: temp_data[0],
      name: 'Sensor 4'
    }, {
      color: "#30c020",
      data: temp_data[1],
      name: 'Sensor 3'
    }, {
      color: "#6060c0",
      data: temp_data[2],
      name: 'Sensor 2'
    }, {
      color: "#9f0ab1",
      data: temp_data[3],
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

} );

var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
  graph: graph,
  legend: legend
} );

var axes = new Rickshaw.Graph.Axis.Time( {
  graph: graph
} );
axes.render();

var slider = new Rickshaw.Graph.RangeSlider({
  graph: graph,
  element: document.getElementById('slider')
});


setInterval( function() {
  graph.update();
  slider.update();
}, 1200 );


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
