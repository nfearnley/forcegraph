function forcegraph(nodeg, linkg, nodes, links)
{
  function rebuild(sim)
  {
    var node = d3.select(nodeg).selectAll(".node")
      .data(sim.nodes())
      .enter()
      .append("g")
      .attr("class", "node");

    var circle = node.append("circle")
      .attr("r", 10);

    var label = node.append("text")
      .attr("dy", ".35em")
      .text(function(d) { return d.nick });

    //var cell = node.append("path")
    //  .attr("class", "cell");

    var link = d3.select(linkg).selectAll(".link")
      .data(sim.force("link").links())
      .enter()
      .append("line")
      .attr("class", "link")
      .attr("stroke", function(d) {
        var strokemin = 0x40;
        var strokemax = 0xFF;
        var countrange = 100;
        var count = Math.min(countrange, d.linkcount)/countrange;
        var stroke = Math.floor(strokemin + (count * (strokemax-strokemin)));
        return "#" + stroke.toString(16).repeat(3);
      });
  }

  function update()
  {
    var node = d3.select(nodeg).selectAll(".node")
      .data(this.nodes());

    //node.select(".cell")
    //  .attr("d", function(d) { return d.length ? "M" + d.join("L") : null });

    node.select("circle")
      .attr("cx", function(d) { return d.x })
      .attr("cy", function(d) { return d.y });

    node.select("text")
      .attr("x", function(d) { return d.x + 8; })
      .attr("y", function(d) { return d.y; });

    d3.select(linkg).selectAll(".link")
      .data(this.force("link").links())
      .attr("x1", function(d) { return d.source.x })
      .attr("y1", function(d) { return d.source.y })
      .attr("x2", function(d) { return d.target.x })
      .attr("y2", function(d) { return d.target.y });
  }

  function setup_zoom()
  {
    var zoom = d3.zoom().on("zoom", function () {
      var w = Math.floor($(this).width() / 2);
      var h = Math.floor($(this).height() / 2);
      d3.select(".foreground").attr("transform",
        "translate("
        + (d3.event.transform.x + w) + ", "
        + (d3.event.transform.y + h) + ")"
        + " scale("
        + d3.event.transform.k + ")");
      d3.selectAll(".nodes .node circle")
        .attr("r", Math.min((1/d3.event.transform.k) * 10, 10));
    })

    var svg = d3.select(".graph");
    svg.call(zoom);

    zoom.transform(svg, d3.zoomTransform(svg.node()));
    $(window).resize(function() {zoom.transform(svg, d3.zoomTransform(svg.node()))});
  }

  setup_zoom();

  var sim = d3.forceSimulation(nodes)
    .force("charge", d3.forceManyBody())
    .force("link", d3.forceLink(links)
      .id(function(d){return d.nickid})
    )
    .force("center", d3.forceCenter(0, 0))
    rebuild(sim)
    sim.on("tick", update);

  return sim;
}
