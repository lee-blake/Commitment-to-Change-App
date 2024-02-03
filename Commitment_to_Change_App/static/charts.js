function generatePieChart(data, pieChartSize, chartContainerSelector){

    const imageSizeX = 600;
    const imageSizeY = 700;

    const radius = Math.min(imageSizeX, imageSizeY) * pieChartSize;
    const color = d3.scaleOrdinal().range(data.map(d => d.color));
     // Create a pie chart function using count as our base
    const pie = d3.pie().value(d => d.count);
    // Create an arc generator for the pie chart
    const arc = d3.arc().innerRadius(0).outerRadius(radius);
    // Select the SVG container
    const svg = d3.select(chartContainerSelector)
        .append("div")
        .classed("svg-container", true)
        .append("svg")
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", `0 0 ${imageSizeX} ${imageSizeY}`)
        .classed("svg-content-responsive", true);

    // Create a group element for the pie chart
    const pieGroup = svg.append("g")
        .attr("transform", `translate(${imageSizeX / 2},${imageSizeY / 1.7})`);

    // Generate the pie chart segments
    const arcs = pie(data);

    // Create and append path elements for each segment
    pieGroup.selectAll("path")
        .data(arcs)
        .enter().append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.color));

    // Add text labels
    pieGroup.selectAll("text")
        .data(arcs)
        .enter().append("text")
        .attr("transform", d => `translate(${arc.centroid(d)})`)
        .attr("text-anchor", "middle")
        .text(d => d.data.label);
    

    // Add legend
    const legend = svg.append("g")
        .attr("transform", `translate(0, 20)`);

    const legendVerticalSpacing = 40;

    legend.selectAll("rect")
        .data(data)
        .enter().append("rect")
        .attr("y", (d, i) => i * legendVerticalSpacing)
        .attr("width", 18)
        .attr("height", 18)
        .attr("fill", d => color(d.color));

    legend.selectAll("text")
        .data(data)
        .enter().append("text")
        .attr("y", (d, i) => i * legendVerticalSpacing + 18)
        .attr("x", 22)
        .text(d => d.legend)
        .classed("pie-chart-legend-text", true);
}