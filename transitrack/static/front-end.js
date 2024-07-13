document.addEventListener('DOMContentLoaded', function () {
    fetchLiveData();
    const tooltip = document.getElementById('tooltip-textbox');
    const svgContainer = document.getElementById('svg-container');
    let circles = [];

    const svgDoc = svgContainer ? svgContainer.querySelector('svg') : null;

    if (svgDoc) {
        circles = svgDoc.querySelectorAll('circle');

        circles.forEach(function (circle) {
            circle.addEventListener('mouseover', function (event) {
                const name = circle.getAttribute('data-name') || 'Data need to show here';
                document.getElementById('textbox-station-name').textContent = name;
                tooltip.style.display = 'block';
            });

            circle.addEventListener('mousemove', function (event) {
                tooltip.style.left = event.pageX + 'px';
                tooltip.style.top = event.pageY + 'px';
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
                                stationCell.textContent = station; // Assuming station is just the name here
                                stationCell.colSpan = 2; // Make the station cells span two columns
                                row.appendChild(stationCell);
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

    function fetchLiveData() {
        fetch('/api/liveCrowdDensity?TrainLine=NSL') // Adjust TrainLine parameter as needed
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log(data); // Log the fetched data to console
                // Handle data as needed (e.g., update UI, process data)
            })
            .catch(error => {
                console.error('Error fetching live data:', error);
            });
    }
});

