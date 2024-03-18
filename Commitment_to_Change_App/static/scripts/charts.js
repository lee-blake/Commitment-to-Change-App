function generateCommitmentStatusPieChart(statusCounts,chartContainerSelector) {
  pieSliceData = [
    {
      count: statusCounts.in_progress,
      color: "legend-color-in-progress",
    },
    {
      count: statusCounts.complete,
      color: "legend-color-complete",
    },
    {
      count: statusCounts.discontinued,
      color: "legend-color-discontinued",
    },
    {
      count: statusCounts.expired,
      color: "legend-color-expired",
    },
  ];
  generatePieChart(pieSliceData, chartContainerSelector);
}

function generatePieChart(pieSliceData, chartContainerSelector) {
  // canvasSize has no effect on the final pie chart size.
  // We draw on a canvas of 1000x1000 just to make sure it's large enough,
  // and use CSS rules to scale it down to a reasonable size for each browser.
  // Scaling down is better than scaling up.
  const canvasSize = 1000;
  const pieRadius = canvasSize / 2;
  const color = d3.scaleOrdinal().range(pieSliceData.map((d) => d.color));
  // Create a pie chart function using count as our base
  const pie = d3.pie().value((d) => d.count);
  // Create an arc generator for the pie chart
  const arc = d3.arc().innerRadius(0).outerRadius(pieRadius);
  // Select the SVG container
  const svg = d3
    .select(chartContainerSelector)
    .append("div")
    .classed("svg-container", true)
    .append("svg")
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", `0 0 ${canvasSize} ${canvasSize}`)
    .classed("svg-content-responsive", true);
  // Create a group element for the pie chart
  const pieGroup = svg
    .append("g")
    .attr("transform", `translate(${canvasSize / 2},${canvasSize / 2})`);
  // Generate the pie chart segments
  const arcs = pie(pieSliceData);
  // Create and append path elements for each segment
  pieGroup
    .selectAll("path")
    .data(arcs)
    .enter()
    .append("path")
    .attr("d", arc)
    .attr("class", (d) => color(d.data.color));
}
