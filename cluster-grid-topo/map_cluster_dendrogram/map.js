var maps = {};

function load_map(map_id, map_json, target_container, params)
{	
		target_container = typeof target_container !== 'undefined' ? target_container : "body";
		
		var height = 400;
		var width = 500;
		var node_attrs_img_prop = false;
		var additional_layers = false;
		var base_tile_layer = false;
		var node_events_img_prop = false;
		var node_opacity = false;
		
		if(params.hasOwnProperty("height"))
			height = params["height"];
		if(params.hasOwnProperty("width"))
			width = params["width"];
		if(params.hasOwnProperty("node_attrs_img"))
			node_attrs_img_prop = params["node_attrs_img"];

		if(params.hasOwnProperty('node_events_2_img'))
			node_events_img_prop = params.node_events_2_img;
			
		if(params.hasOwnProperty("additional_layers"))
			additional_layers = params["additional_layers"];
		
		// base layer is always the first one in the layers array
		if(params.hasOwnProperty('base_tile_layer'))
			base_tile_layer = params.base_tile_layer;
		
		
		if(params.hasOwnProperty('node_opacity'))
			node_opacity = params.node_opacity;
	
		var map_decorations_container = d3.select(target_container).append("div")
										.attr("id","map_decorations_container_"+map_id)
										.attr("class", "map_decorations_container");
	
		var map_container = d3.select("#map_decorations_container_" + map_id).append("div")
							.attr("id","map_container_"+map_id)
							.style({height:height + "px", width:width + "px", float:"left"}); // expose width/height as parameters?
	
		//var map = L.map("map_container_"+map_id, { attributionControl:false, crs: L.CRS.EPSG4326 }).setView([47.5826601,-122.1533733], 13);
		var map = L.map("map_container_"+map_id, { attributionControl:false, crs: L.CRS.EPSG3857 }).setView([47.5826601,-122.1533733], 13);
		
		mapLink = '<a href="http://openstreetmap.org">OpenStreetMap</a>'; 
		



		/*
		tile_layer = L.tileLayer('http://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
	   	  }).addTo(map);
	   	  */
		var tile_layer;
		if(base_tile_layer)
			tile_layer = base_tile_layer;
		else
		{
			tile_layer = L.tileLayer('http://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png', {
				attribution: '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
		   	  })
		}
		
		tile_layer.addTo(map);
		
		/* Initialize the SVG layer */
		map._initPathRoot();
		
		var svg = d3.select("#map_container_"+map_id).select("svg")
		  .attr("id", map_id);
		
		/* add flow arrow support */
		
		svg.append("svg:defs")
		.append("svg:marker")
		.attr("id", "arrow")	
		.attr("refX", 2)
		.attr("refY", 6)
		.attr("markerWidth", 5)
		.attr("markerHeight", 5)
		.attr("orient", "auto")
		.append("svg:path")
		.attr("d", "M2,2 L2,11 L10,6 L2,2");
		
		maps[map_id] = {
				"map":map,
				"layers":[tile_layer]
				}
		
		// add any additional layers specified (e.g. server side wms QGIS)
		if(additional_layers)
		{
			for(var i = 0; i < additional_layers.length; i++)
			{
				maps[map_id]["layers"].push(additional_layers[i]);
				additional_layers[i].addTo(map)
			}
		}
		
		
		d3.json(map_json, function(map_nodes){ 
		
			var markers = [];
			var nodes = [];
			
			// for now have a limit of three attribtues to image (i.e. three arrays of nodes) due to geometry limitations; might be able to go to up to 6 with current layout?
			var nodes_2_imgs = {};
			var nodes_2_img = [];
						
			map_nodes.forEach(function(d) {
				
				
				markers.push(new L.LatLng(d.Latitude, d.Longitude))
				nodes.push({
								coor:new L.LatLng(d.Latitude, d.Longitude), 
								node:d
								});
				
				/*
				 * 
				 * node_attrs_img_prop sample format:
				 * 
				 * var node_attrs_img_prop = [
                      {
                    	  'node_attr_img':"Received_ITN",
                    	  'img_scale':d3.scale.threshold().domain([0, 10]).range([0, 1, 2, 3]),
                    	  'img_src':['imgs/net.png', 'imgs/net.png', 'imgs/net.png', 'imgs/net.png']
                      },
				 * 
				 */
				if(node_attrs_img_prop)
				{
					nodes_2_img.push({
						coor:new L.LatLng(d.Latitude, d.Longitude), 
						node:d
					});
				}
			})
			
			for (var i = 0; i < node_attrs_img_prop.length; i ++)
			{		
				
				nodes_2_imgs[node_attrs_img_prop[i]['node_attr_img']] = {};
				nodes_2_imgs[node_attrs_img_prop[i]['node_attr_img']]['nodes'] = nodes_2_img;
			}	
			
			
			//maps[map_id]["nodes_2_imgs"] = nodes_2_imgs;
			//maps[map_id]["nodes"] = nodes;
			
			var bounds = new L.LatLngBounds(markers);
			
			
			/* 
			 * Should nodes be displayed on load_map?
			 * Perhaps the most generic map should only contain 
			 * a base map layer and avoid rendering additional objects?
			 * 
			 * This behavior can easily be refactored.
			 */
			
			g = svg.append("g")
				.attr("class","map")
				.attr("id","svgNodesContainer");
			
			var node = g.selectAll("[node-group="+map_id+"]")
			.data(nodes)
			.enter().append("circle")
			.attr("r", 3)  
			.attr("id", function(d) {return d.node.NodeLabel})
			.attr("ttl",100)
			.attr("opacity", function(d){ if(node_opacity) return node_opacity; else return 0.8; })
			.attr("node-group", map_id)
			.attr("class", function(d) {return "unselected-map-node " + "cluster-" + d.node.ClusterLabel});
			
			for (var i = 0; i < node_attrs_img_prop.length; i ++)
			{	
				var node_attr_img = node_attrs_img_prop[i]['node_attr_img'];
				var img_scale = node_attrs_img_prop[i]['img_scale'];
		        var img_src = node_attrs_img_prop[i]['img_src'];

		        // setup an image pattern if node attribute to image map has been specified and patterns have not been created before
		        var pattern_svg = d3.select("body").append("svg").attr("id", "pattern_" + node_attr_img);
		        var pattern_defs = pattern_svg.append("defs").attr("id", "defs_" + node_attr_img);
		        pattern_defs.selectAll("pattern")
				.data(img_scale.range())
				.enter().append("pattern")
					.attr("id", function (d) { return node_attr_img + "_" + d; })
					.attr("x", 0)
					.attr("y", 0)
					.attr("height", 17)
					.attr("width", 17)
					.insert("image")
					  .attr("x", 0)
					  .attr("y", 0)
					  .attr("height", 20)
					  .attr("width", 20)
					  .attr("xlink:href", function (d) { return img_src[d]; });
				
				
		        var nodes = nodes_2_imgs[node_attr_img]['nodes'];
				nodes_2_imgs[node_attr_img]['markers'] = g.selectAll("." + node_attr_img)
				.data(nodes)
				.enter().append("circle")
				.attr("r", 6.5)  // might expose that as a parameter
				.attr("id", function(d) {return "attr" + node_attr_img  + "_" + get_node_key(d.node.NodeLabel, map_id)})
				.attr("class", function(d) {return node_attr_img  })
				//.attr("opacity", 1.0)
				//.attr("fill", "red")
				.attr("opacity", 0.0)
				.attr("ttl", 0);
			}
			

			if(node_events_img_prop)
			{
				for (var i = 0; i < node_events_img_prop.length; i ++)
				{
					var node_event_img = node_events_img_prop[i]['node_event_img'];
					var img_scale = node_events_img_prop[i]['img_scale'];
					var img_src = node_events_img_prop[i]['img_src'];

					// setup an image pattern if node attribute to image map has been specified and patterns have not been created before
			        var pattern_svg = d3.select("body").append("svg").attr("id", "pattern_event_" + node_event_img);
			        var pattern_defs = pattern_svg.append("defs").attr("id", "defs_event_" + node_event_img);
			        pattern_defs.selectAll("pattern")
					.data(img_scale.range())
					.enter().append("pattern")
						.attr("id", function (d) { return "event" + node_event_img + "_" + d; })
						.attr("x", 0)
						.attr("y", 0)
						.attr("height", "100%")
						.attr("width", "100%")
						.attr("viewBox", "0 0 1 1")
						.attr("preserveAspectRatio", "xMidYMid slice")
						.insert("image")
						  .attr("x", 0)
						  .attr("y", 0)
						  .attr("height", 1)
						  .attr("width", 1)
						  .attr("preserveAspectRatio", "xMidYMid slice")
						  .attr("xlink:href", function (d) { return img_src[d]; });
				}
			
			}
				
			map.on("viewreset", update);
			update();
			
			
			function update() {
				node.attr("transform", 
				function(d) { 
					return get_node_map_position(d.node, map);
				})	
				
				for (var i = 0; i < node_attrs_img_prop.length; i ++)
				{
					var node_attr_img = node_attrs_img_prop[i]['node_attr_img'];
			        var node_2_img = nodes_2_imgs[node_attr_img]['markers']
			        
					// again, currently only up to four attributes would be displayed due to geometry
					var offset_x = 0;
					var offset_y = 0;
					
					if(i == 0)
					{
						offset_x = -5;
						offset_y = -5;
					}
					else
					if(i == 1)
					{
						offset_x = 5;
						offset_y = -5;
					}
					else
					if(i == 2)
					{
						offset_x = -5;
						offset_y = 5;
					}
					else
					if(i == 3)
					{
						offset_x = 5;
						offset_y = 5;
					}
					else
						continue;
					
					node_2_img.attr("transform", 
						function(d) { 
							return "translate("+ 
								(map.latLngToLayerPoint(d.coor).x + offset_x) +","+ 
								(map.latLngToLayerPoint(d.coor).y + offset_y) +")";
						})	
				}
			}
			
			map.fitBounds(bounds);
	
		});// end d3.json(...)
	
	//style_map(map_id, map_json, {});
	return;
}


/*
 * helper function: given node entry return node transform so that the node is properly position on a leaflet map
 */
function get_node_map_position(node, map)
{
	var coor = new L.LatLng(node.Latitude, node.Longitude);
	
	return "translate("+ 
		map.latLngToLayerPoint(coor).x +","+ 
		map.latLngToLayerPoint(coor).y +")";
}


/*
 * helper function: given node entry return node map layer x and y coordinates (coorespondign to the node's lat and long coordinates)
 */
function get_node_map_x_y_coors(node, map)
{
	var coor = new L.LatLng(node.Latitude, node.Longitude);
	
	return {"x":map.latLngToLayerPoint(coor).x, "y":map.latLngToLayerPoint(coor).y};
}