function generatePieChart(data, chartContainerSelector){
    const pieChartSize = 0.45;

    const imageSizeX = 600;
    const imageSizeY = 600;

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
        .attr("transform", `translate(${imageSizeX / 2},${imageSizeY / 2})`);

    // Generate the pie chart segments
    const arcs = pie(data);

    // Create and append path elements for each segment
    pieGroup.selectAll("path")
        .data(arcs)
        .enter().append("path")
        .attr("d", arc)
        .attr("class", d => color(d.data.color));
}