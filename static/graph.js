function renderGraph(graph) {
  const svg = d3.select("svg");
  svg.selectAll("*").remove();

  const width = 600, height = 400;

  const simulation = d3.forceSimulation(graph.nodes)
    .force("link", d3.forceLink(graph.edges).id(d => d.id).strength(d => d.weight))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2));

  const link = svg.append("g")
    .selectAll("line")
    .data(graph.edges)
    .enter()
    .append("line")
    .style("stroke-width", d => d.weight * 3);

  const node = svg.append("g")
    .selectAll("circle")
    .data(graph.nodes)
    .enter()
    .append("circle")
    .attr("r", 10)
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
  });
}
