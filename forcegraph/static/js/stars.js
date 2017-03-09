function starfield(field, count=10000, low=32, high=160, curve=8)
{
  low = Math.min(Math.max(low, 0), 255);
  high = Math.min(Math.max(high, low), 255);
  var svg = $(field).parents("svg");
  var w = svg.width();
  var h = svg.height();
  var stars = [];
  for (var x = 0; x < count; x++)
  {
    stars.push({
      "x": Math.random() * w,
      "y": Math.random() * h,
      "b": Math.floor(low + ((Math.random() ** curve) * (high - low)))
    });
  }

  fieldpoints = d3.select(field).selectAll("circle")
    .data(stars);
  fieldpoints.enter().append("circle")
    .merge(fieldpoints)
    .attr("r", 1)
    .attr("fill", function (d) {return "#" + d.b.toString(16).repeat(3)})
    .attr("cx", function (d) {return d.x})
    .attr("cy", function (d) {return d.y});
  fieldpoints.exit().remove();
}
