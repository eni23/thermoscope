var main_graph = {
  data: [],
  graph: {}
};

var last_temp_values = [false,false,false,false];

var init_main_graph = function(){
  smoothPlotter.smoothing = 0.3
  var d = new Date();
  main_graph.data.push([d, 0.0, 0.0, 0.0, 0.0]);
  main_graph.graph = new Dygraph(
    $("#main-graph").get(0),
    main_graph.data,
    {
      gridLineColor: 'rgb(193, 193, 193)',
      axisLineColor: 'rgb(193, 193, 193)',
      axisLabelColor: 'rgb(193, 193, 193)',
      drawPoints: false,
      showRoller: false,
      strokeWidth: 3,
      valueRange: [0.0, 60.00],
      labels: ['time','1','2','3','4'],
      plotter: smoothPlotter,
      connectSeparatedPoints: true,
    }
  );


  var dragSlider = $("#range-slider").get(0);

  noUiSlider.create(dragSlider, {
  	start: [ 0, 60 ],
  	behaviour: 'drag',
  	connect: true,
  	range: {
  		'min':  -50,
  		'max':  130
  	},
    step: 1
  });
  dragSlider.noUiSlider.on('update', function(){
  	var fdata = this.get();
    var data = [ parseInt(fdata[0]), parseInt(fdata[1]) ];
    $("#range-min").html(data[ 0 ]);
    $("#range-max").html(data[ 1 ]);
    main_graph.graph.updateOptions( { 'valueRange': fdata } );
  });


}

setInterval( function() {
  main_graph.graph.updateOptions( { 'file': main_graph.data } );
}, 250 );




var add_temp_data = function(sensor_number, temp) {
  var ts = new Date();
  var aa = []
  aa[0] = ts;
  for (i=1;i<5;i++){
    aa[i]=last_temp_values[i-1];
  }
  aa[sensor_number] = temp;
  last_temp_values[sensor_number-1] = temp;
  main_graph.data.push(aa);

}

$(document).ready(
  function(){
    init_main_graph();
  }
);
