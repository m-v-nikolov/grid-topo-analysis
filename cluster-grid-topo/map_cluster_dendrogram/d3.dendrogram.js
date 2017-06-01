var ix = 0,
    duration = 750,
    root_d,
    tree,
    diagonal,
    vis;

var selected_dendro_node = false;

if (!d3)
{ throw "d3 wasn't included!" };


(function ()
{
      d3.phylogram = {}
      d3.phylogram.rightAngleDiagonal = function ()
      {
        var projection = function(d) { return [d.y, d.x]; }
    
        var path = function (pathData)
        {
          return "M" + pathData[0] + ' ' + pathData[1] + " " + pathData[2];
        }
    
        function diagonal(diagonalPath, i)
        {
          var source = diagonalPath.source,
              target = diagonalPath.target,
              midpointX = (source.x + target.x) / 2,
              midpointY = (source.y + target.y) / 2,
              pathData = [source, {x: target.x, y: source.y}, target];
          pathData = pathData.map(projection);
          return path(pathData)
        }
    
        diagonal.projection = function (x)
        {
          if (!arguments.length) return projection;
          projection = x;
          return diagonal;
        };
    
        diagonal.path = function (x)
        {
          if (!arguments.length) return path;
          path = x;
          return diagonal;
        };
    
        return diagonal;
      }
  
      d3.phylogram.radialRightAngleDiagonal = function ()
      {
        return d3.phylogram.rightAngleDiagonal()
          .path(function (pathData)
          {
            var src = pathData[0],
                mid = pathData[1],
                dst = pathData[2],
                radius = Math.sqrt(src[0]*src[0] + src[1]*src[1]),
                srcAngle = d3.phylogram.coordinateToAngle(src, radius),
                midAngle = d3.phylogram.coordinateToAngle(mid, radius),
                clockwise = Math.abs(midAngle - srcAngle) > Math.PI ? midAngle <= srcAngle : midAngle > srcAngle,
                rotation = 0,
                largeArc = 0,
                sweep = clockwise ? 0 : 1;
            return 'M' + src + ' ' +
              "A" + [radius,radius] + ' ' + rotation + ' ' + largeArc+','+sweep + ' ' + mid +
              'L' + dst;
          })
          .projection(function (d)
          {
            var r = d.y, a = (d.x - 90) / 180 * Math.PI;
            return [r * Math.cos(a), r * Math.sin(a)];
          })
      }
  
      // Convert XY and radius to angle of a circle centered at 0,0
      d3.phylogram.coordinateToAngle = function (coord, radius)
      {
        var wholeAngle = 2 * Math.PI,
            quarterAngle = wholeAngle / 4
    
        var coordQuad = coord[0] >= 0 ? (coord[1] >= 0 ? 1 : 2) : (coord[1] >= 0 ? 4 : 3),
            coordBaseAngle = Math.abs(Math.asin(coord[1] / radius))
    
        // Since this is just based on the angle of the right triangle formed
        // by the coordinate and the origin, each quad will have different 
        // offsets
        switch (coordQuad)
        {
          case 1:
            coordAngle = quarterAngle - coordBaseAngle
            break
          case 2:
            coordAngle = quarterAngle + coordBaseAngle
            break
          case 3:
            coordAngle = 2*quarterAngle + quarterAngle - coordBaseAngle
            break
          case 4:
            coordAngle = 3*quarterAngle + coordBaseAngle
        }
        return coordAngle
      }

      d3.phylogram.styleTreeNodes = function (vis)
      {
        colors = ["#3366cc", "#dc3912", "#ff9900", "#109618", "#990099", "#0099c6", "#dd4477", "#66aa00", "#b82e2e", "#316395", "#994499", "#22aa99", "#aaaa11", "#6633cc", "#e67300", "#8b0707", "#651067", "#329262", "#5574a6", "#3b3eac"];

        vis.selectAll('g.node.leaf')
          .append("svg:circle")
            .attr("r", "0.5em")
            .attr('stroke',  'red')
            //.attr("fill", function(d){return colors[d.name%20];})  
            .attr('stroke-width', '0px');

        vis.call(d3.behavior.zoom().scale(0.9).scaleExtent([0.1, 3]).on("zoom", zoom)).on("dblclick.zoom", null);

        vis.selectAll('g.node.inner')
          .append('svg:circle')
          .attr('r', "0.25em")
          .attr('fill', 'green')

        vis.selectAll('g.node.root')
          .append('svg:circle')
            .attr("r", "2em")
            //.attr('fill', 'steelblue')
            .attr('stroke', 'black')
            .attr('stroke-width', '2px');

        function zoom()
        {
         vis.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
        } 
      }
  
      function scaleBranchLengths(nodes, w)
      {
        // Visit all nodes and adjust y pos width distance metric
          var visitPreOrder = function (root, callback)
          {
          callback(root)
          if (root.children)
          {
            for (var i = root.children.length - 1; i >= 0; i--){
              visitPreOrder(root.children[i], callback)
            };
          }
        }
          visitPreOrder(nodes[0], function (node)
          {
            node.rootDist = (node.parent ? node.parent.rootDist : 0) + (node.length || 0)
          })
        var rootDists = nodes.map(function(n) { return n.rootDist; });
        var yscale = d3.scale.linear()
          .domain([0, d3.max(rootDists)])
          .range([0, w]);
        visitPreOrder(nodes[0], function (node)
        {
          node.y = yscale(node.rootDist)
        })
        return yscale
      }
  

      d3.phylogram.build = function (selector, nodes, options)
      {
        options = options || {}
        var w = options.width || d3.select(selector).style('width') || d3.select(selector).attr('width'),
            h = options.height || d3.select(selector).style('height') || d3.select(selector).attr('height'),
            w = parseInt(w),
            h = parseInt(h);
        tree = options.tree || d3.layout.cluster()
          .size([h, w])
          .sort(function(node) { return node.children ? node.children.length : -1; })
          .children(options.children || function (node)
          {
            return node.branchset
          });

        diagonal = options.diagonal || d3.phylogram.rightAngleDiagonal();
        vis = options.vis || d3.select(selector).append("svg:svg")
            .attr("width", w + 300)
            .attr("height", h + 30)
          .append("svg:g")
            .attr("transform", "translate(20, 20)");
    
        var nodes = tree(nodes);
    
        if (options.skipBranchLengthScaling)
        {
          var yscale = d3.scale.linear()
            .domain([0, w])
            .range([0, w]);
        }
        else
        {
          var yscale = scaleBranchLengths(nodes, w)
        }
    
     
        var link = vis.selectAll("path.link")
            .data(tree.links(nodes))
          .enter().append("svg:path")
            .attr("class", "link")
            .attr("d", diagonal)
            .attr("fill", "none")
            //.attr("stroke", "#aaa")
	    .attr("stroke","pink")
            .attr("stroke-width", "1px");

      
   
        nodes.forEach(function(node)
		        {
    			    if(node.depth==0)
	   	    		    root_d = node;	
		        }
        ) 
    
        root_d.x0 = root_d.x;
        root_d.y0 = root_d.y;


    
        function collapse(d)
        {
            if (d.children || d.branchset)
            {
	            d._branchset = d.branchset;
	            d.branchset = null;
                d._children = d.children;
                d._children.forEach(collapse);
                d.children = null;
            }
         }
    
        //root_d.children.forEach(collapse);  
        collapse(root_d);

        update(root_d);
     
        return {tree: tree, vis: vis}
      }


     function update(source)
     {

      // Compute the new tree layout.
      var nodes = tree.nodes(root_d).reverse(),
          links = tree.links(nodes);
 
      var node = vis.selectAll("g.node")
 	      .data(nodes, function(d) { return d.id || (d.id = ++ix); });

      var nodeEnter = node.enter().append("g")
            .attr("class", function(n) {
              if (n.children) {
                if (n.depth == 0) {
	          root_d = n;
	          root_d.x0 = n.x;
	          root_d.y0 = n.y;
                  return "node root"
                } else {
	          n.x0 = n.x;
	          n.y0 = n.y;
                  return "node inner"
                }
              } else {
	          n.x0 = n.x;
	          n.y0 = n.y;	  
                return "node leaf"
              }
            })
            .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
	    .on("click", click);

      nodeEnter.append("circle")
          .attr("r", 2)
          .style("fill", function(d) { return d._children ? "green" : "#fff"; });

      // Transition nodes to their new position.
      var nodeUpdate = node.transition()
          .duration(duration)
          .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

      nodeUpdate.select("circle")	
          .attr("r", 4.5)
          .style("fill", function(d) { return d._children ? "green" : "#fff"; }); 


      // Transition exiting nodes to the parent's new position.
  
      var nodeExit = node.exit().transition()
          .duration(duration)
          .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
          .remove();


      nodeExit.select("circle")
          .attr("r", 2);


      d3.phylogram.styleTreeNodes(vis)
  

      var link = vis.selectAll("path.link").data(tree.links(nodes));

      // Enter any new links at the parent's previous position.
     link.enter().append("svg:path")
            .attr("class", "link")
            .attr("d", diagonal)
            .attr("fill", "none")
            //.attr("stroke", "#aaa")
	        .attr("stroke","darkgrey")
            .attr("stroke-width", "2px");
  

      // Transition links to their new position.
      link.transition()
          .duration(duration)
          .attr("d", diagonal);

      // Transition exiting links to the parent's new position.
      link.exit().transition()
          .duration(duration)
          .attr("d", function (d)
          {
            var o = {x: source.x, y: source.y};
            return diagonal({source: o, target: o});
          })
          .remove();
  

      // Stash the old positions for transition.
      nodes.forEach(function (d)
      {
        d.x0 = d.x;
        d.y0 = d.y;
      });
    }

    // Toggle children on click.
     function click(d)
     {
         if (d.children)
         {
            d._branchset = d.branchset;
            d._children = d.children;
            d.branchset = null;
            d.children = null;
         }
         else
         {
            d.children = d._children;
            d.branchset = d._branchset;
            d._children = null;
            d._branchset = null;
        }

      update(d);
   
      if(selected_dendro_node) 
      {
	      d3.select(selected_dendro_node).attr("fill", "black");
	      d3.select(this).attr("fill", "red");
      }
      else 
	    d3.select(this).attr("fill", "red");

      var leafDescendants = getLeafDescendants(d);

      // unselect all previously selected nodes
      d3.selectAll(".selected-map-node")
	      .classed("selected-map-node", false)
              .classed("unselected-map-node", true);


      // select all leaf descendants of the clicked node on the map  
      leafDescendants.forEach(function (d) {
          d3.selectAll(".cluster-" + d.name)
              .classed("unselected-map-node", false)
              .attr("class", "selected-map-node " + "cluster-" + d.name);
      });
    
      selected_dendro_node = this;
    }

    // get the leaf descendants of a node
    function getLeafDescendants(node)
    {
       var leafDescendants = [];

       var visitPreOrder = function (root, callback)
       {
          callback(root);
          if(root.children || root._children)
          {
	          if (root.children) 
	          {
        	    for (var i = root.children.length - 1; i >= 0; i--)
	    	    {
	              visitPreOrder(root.children[i], callback);
        	    }
	          }
	          else
	          if (root._children) 
	          {
        	    for (var i = root._children.length - 1; i >= 0; i--)
		        {
	              visitPreOrder(root._children[i], callback);
        	    }
	          }
          }
          else
	        leafDescendants.push(root);
        }

       visitPreOrder(node, function (node) {
           return;
       });

        return leafDescendants;
    }

}());
