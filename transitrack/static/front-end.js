document.addEventListener('DOMContentLoaded', function () {
    fetchLiveCrowdData();
    const tooltip = document.getElementById('tooltip-textbox');
    const svgContainer = document.getElementById('svg-container');
    let circles = [];
    const combinedData = [];

    const svgDoc = svgContainer ? svgContainer.querySelector('svg') : null;

    if (svgDoc) {
        circles = svgDoc.querySelectorAll('circle');
        circles.forEach(function (circle) {

            circle.addEventListener('mouseover', function (event) {
                tooltip.querySelectorAll('.container-sm').forEach(function (node) {
                    node.remove();
                });
                const name = circle.getAttribute('data-name') || 'Data need to show here';
                document.getElementById('textbox-station-name').textContent = name;
                tooltip.style.display = 'block';
                const nodeDataValue = circle.getAttribute('data-value').split(',');
                const newHeight = 100 + nodeDataValue.length * 100;
                let className, width;
                tooltip.style.height = `${newHeight}px`;

                nodeDataValue.forEach(value => {

                    const crowdLevelValue = getCrowdDensityLevel(value);
                    stationlineCode = filterCharacter(value);
                    console.log(stationlineCode);
                    if (crowdLevelValue == 'l') {
                        className = 'bg-success';
                        width = '33%';
                    }
                    else if (crowdLevelValue == 'm') {
                        className = 'bg-warning';
                        width = '66%';
                    }
                    else if (crowdLevelValue == 'h') {
                        className = 'bg-danger';
                        width = '100%';
                    }


                    const LiveCrowdDiv = document.createElement('div');
                    LiveCrowdDiv.classList.add('container-sm');

                    const stationLineLogo = document.createElement('img');
                    stationlineName = stationLine(stationlineCode);
                    console.log('station line name:', stationlineName);
                    stationLineLogo.src = `static/assets/${stationlineName}.png`;
                    stationLineLogo.alt = stationlineName;

                    const liveCrowdLbl = document.createElement('p');
                    liveCrowdLbl.classList.add('p');
                    liveCrowdLbl.textContent = 'crowd level: ';

                    const progressBarContainer = document.createElement('div');
                    progressBarContainer.classList.add('progress');

                    const progressBar = document.createElement('div');
                    progressBar.classList.add('progress-bar');
                    progressBar.id = 'liveCrowdLevelValue';
                    progressBar.classList.add(className);
                    progressBar.style.width = width;
                    const breakLine = document.createElement('br');

                    progressBarContainer.appendChild(progressBar);
                    progressBarContainer.appendChild(breakLine);

                    LiveCrowdDiv.appendChild(document.createElement('br'));
                    LiveCrowdDiv.appendChild(stationLineLogo);
                    LiveCrowdDiv.appendChild(liveCrowdLbl);
                    LiveCrowdDiv.appendChild(progressBarContainer);

                    tooltip.appendChild(LiveCrowdDiv);
                })

            });

            circle.addEventListener('mousemove', function (event) {
                const tooltipWidth = tooltip.offsetWidth;
                const tooltipHeight = tooltip.offsetHeight;
                const pageX = event.pageX;
                const pageY = event.pageY;
                const containerRect = svgContainer.getBoundingClientRect();

                let tooltipX = pageX;
                let tooltipY = pageY;

                if (pageX + tooltipWidth > containerRect.right) {
                    tooltipX = pageX - tooltipWidth;
                }

                if (pageY + tooltipHeight > containerRect.bottom) {
                    tooltipY = pageY - tooltipHeight;
                }

                tooltip.style.left = tooltipX + 'px';
                tooltip.style.top = tooltipY + 'px';
            });

            circle.addEventListener('mouseout', function () {
                tooltip.style.display = 'none';
            });
        });
    } else {
        console.error("SVG document not found!");
    }

    const fromBox = document.getElementById('fromBox');
    const toBox = document.getElementById('toBox');

    fromBox.addEventListener('input', function () {
        performSearch(fromBox.value, 'from');
    });

    toBox.addEventListener('input', function () {
        performSearch(toBox.value, 'to');
    });

    const submitButton = document.getElementById('submitButton');
    if (submitButton) {
        submitButton.addEventListener('click', function (event) {
            event.preventDefault();

            const fromBoxValue = document.getElementById('fromBox').value.trim().toLowerCase();
            const toBoxValue = document.getElementById('toBox').value.trim().toLowerCase();
            const algorithm = document.getElementById('select_box').value.trim().toLowerCase();

            if (fromBoxValue && toBoxValue && algorithm) {
                fetch(`/api/${algorithm}/?start=${fromBoxValue}&end=${toBoxValue}`)
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(data => { throw new Error(data.error); });
                        }
                        return response.json();
                    })
                    .then(data => {
                        alert(JSON.stringify(data))
                        if (data.route !== 'null') {
                            resetPath();
                            markPath(data.route);
                            
                            // clear
                            const resultsElement = document.getElementById('results');
                            resultsElement.innerHTML = '';
                        
                            // table
                            const table = document.createElement('table');
                            table.style.width = '100%'; // Set table width
                            table.setAttribute('border', '1');
                        
                            const thead = document.createElement('thead');
                            const headerRow = document.createElement('tr');
                            const stationHeader = document.createElement('th');
                            stationHeader.textContent = 'Station';
                            stationHeader.colSpan = 2; // Make the header span two columns
                            headerRow.appendChild(stationHeader);
                            thead.appendChild(headerRow);
                            table.appendChild(thead);
                        
                            const tbody = document.createElement('tbody');
                            data.route.forEach(station => {
                                const row = document.createElement('tr');
                                const stationCell = document.createElement('td');
                                stationCell.colSpan = 2; // Span across two columns if needed
                            
                                // Create a text node for the station name to add before the image
                                const stationText = document.createTextNode(station + " "); // Adding a space for separation
                                stationCell.appendChild(stationText);
                            
                                // Image element
                                const stationImage = document.createElement('img');
                                stationImage.src = 'path/to/your/image.png'; // Set the source of your image here
                                stationImage.style.width = '50px'; // Adjust size as needed
                                stationImage.style.height = 'auto';
                                stationImage.style.marginLeft = '10px'; // Add some space between the text and the image
                            
                                // Append the image to the same cell as the station name
                                stationCell.appendChild(stationImage);
                            
                                // Append the cell to the row
                                row.appendChild(stationCell);
                            
                                // Append the row to the tbody
                                tbody.appendChild(row);
                            });
                        
                            // appending
                            const totalDurationRow = document.createElement('tr');
                            const totalDurationCell = document.createElement('td');
                            totalDurationCell.textContent = 'Total Duration';
                            const durationCell = document.createElement('td');
                            durationCell.textContent = data.duration + ' minutes';
                            totalDurationRow.appendChild(totalDurationCell);
                            totalDurationRow.appendChild(durationCell);
                            tbody.appendChild(totalDurationRow);
                        
                            table.appendChild(tbody);
                            resultsElement.appendChild(table);
                        } else {
                            document.getElementById('results').innerHTML += '<div>No route found.</div>';
                        }                            
                    })
                    .catch(error => {
                        document.getElementById('results').innerHTML = '';
                        document.getElementById('results').innerHTML = 'Error: ' + error.message;
                        console.error('Error:', error);
                    });
            } else {
                alert('Please enter both "From" and "To" locations.');
            }
        });
    } else {
        console.error("Submit button not found!");
    }

    function performSearch(query, type) {
        if (query.length === 0) {
            return;
        }
    
        let endpoint = type === 'from' ? '/api/search' : '/api/binarysearch';
    
        fetch(`${endpoint}?query=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log(`Received ${type} search results:`, data.results);
                if (type === 'from') {
                    fromBox.setAttribute('list', 'from-datalist');
                    updateDatalist('from-datalist', data.results);
                } else {
                    toBox.setAttribute('list', 'to-datalist');
                    updateDatalist('to-datalist', data.results);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
    
    function updateDatalist(datalistId, items) {
        const datalist = document.getElementById(datalistId);
        datalist.innerHTML = ''; // Clear any existing options
    
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            datalist.appendChild(option);
        });
    }

    function markPath(route) {
        if (!circles.length) {
            console.error("No circles found!");
            return;
        }

        // Highlight the path
        circles.forEach(circle => {
            const stationName = circle.getAttribute('data-name');
            if (stationName && route.includes(stationName)) {
                circle.setAttribute('fill', 'black'); // Example of highlighting the path by changing fill color
            }
        });
    }

    function resetPath() {
        // Reset all circles to no fill
        circles.forEach(circle => {
            circle.setAttribute('fill', '');
        });
    }

    async function fetchLiveCrowdData() {
        const MRTLines = ['NSL', 'CCL', 'CEL', 'CGL', 'DTL', 'EWL', 'NEL', 'BPL', 'SLRT', 'PLRT'];

        for (const line of MRTLines) {
            try {
                const response = await fetch(`/api/liveCrowdDensity?TrainLine=${line}`);
                if (!response.ok) {
                    throw new Error(`Failed to collect ${line}`);
                }
                const data = await response.json();
                // Ensure data.value is an array before using the spread operator
                if (data && Array.isArray(data.value)) {
                    combinedData.push(...data.value); // Combine data into the main array
                } else {
                    console.error(`Data for ${line} is not in expected format`, data);
                }
            } catch (error) {
                console.error('Error fetching live crowd data:', error);
            }
        }

        console.log(combinedData); // Log the combined data to console
        
    }

    function getCrowdDensityLevel(MRTcode) {
        const stationData = combinedData.find(content => content.Station === MRTcode);
        console.log('MRTcode:', MRTcode);
        console.log('Station Data:', stationData);
        console.log(stationData);
        return stationData ? stationData.CrowdLevel : 'station not found';
    }

    function filterCharacter(stationCode) {
        return stationCode.replace(/[^a-zA-Z]/g, '');
    }

    function stationLine(initial) {
        if (initial == 'TE') 
        {
            return "Thomson–East Coast Line";
        }
        else if (initial == "NS") 
        {
            return "North-South Line";
        }
        else if (initial == "EW") 
        {
            return "East-West Line";
        }
        else if (initial == "CC") 
        {
            return "Circle Line";
        }
        else if (initial == "DT") 
        {
            return "Downtown Line";
        }
        else if (initial == "NE") 
        {
            return "North-East line";
        }
        else if (initial == "CG") 
        {
            return "Changi Airport Line";
        }
        else if (initial == "PE" || initial == "PW" || initial == "PTC" )
        {
            return "Punggol LRT";
        }
        else if (initial == "SE" || initial == "SW" || initial == "STC" )
        {
            return "Sengkang LRT";
        }
        else if (initial == "BP")
        {
            return "Bukit Panjang LRT";
        }
    }

    setInterval(function () {
        location.reload();
    }, 1800000);
});

