document.addEventListener('DOMContentLoaded', function () {
    //fetchLiveCrowdData();
    fetchRouteInfo();
    const tooltip = document.getElementById('tooltip-textbox');
    const svgContainer = document.getElementById('svg-container');
    let circles = [];
    const combinedData = [];
    const routeData = [];

    const svgDoc = svgContainer ? svgContainer.querySelector('svg') : null;

    //Mainly consist of the front end design
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
                        console.log('hello' + getMostOptimalAlgorithm(fromBoxValue, toBoxValue));
                        return response.json();
                    })
                    .then(data => {
                        if (data.route !== 'null') {
                            resetPath();
                            markPath(data.route);


                            //create route and analysis section
                            const resultInfoSection = document.getElementById('result');
                            resultInfoSection.innerHTML = '';

                            const resultContainer = document.createElement('div');
                            resultContainer.className = 'col results-container scrollbar';
                            resultContainer.id = 'style-1';

                            const analysisContainer = document.createElement('div');
                            analysisContainer.className = 'col';
                            analysisContainer.id = 'analysis';

                            resultInfoSection.appendChild(resultContainer);
                            resultInfoSection.appendChild(analysisContainer);


                            //display route section
                            const resultsElement = document.getElementById('style-1');
                            resultsElement.innerHTML = '';

                            const resultStartLbl = document.createElement('p');
                            resultStartLbl.textContent = "Start";

                            const resultUL = document.createElement('ul');

                            let currentStation = "";

                            data.route.forEach((station, index) => {
                                const nextStation = index < data.route.length - 1 ? data.route[index + 1] : null;
                                const stationInfo = (searchRouteInfo(station, nextStation));

                                const resultLI = document.createElement('li');

                                const resultTime = document.createElement('span');
                                resultTime.textContent = stationInfo ? stationInfo.duration + ' min' : 'Total: ' + data.duration + ' min';
                                resultLine = stationInfo ? stationInfo.line : 'test';

                                const resultStationName = document.createElement('div');
                                resultStationName.textContent = station;

                                if (nextStation != null) {
                                    currentStation = StationIcon(resultLine);
                                }
                                const stationImage = document.createElement('img');
                                stationImage.src = `static/assets/${currentStation}.png`;
                                stationImage.style.width = '50px';
                                stationImage.style.height = 'auto';
                                stationImage.style.marginLeft = '10px';

                                resultLI.appendChild(resultTime);
                                resultLI.appendChild(resultStationName);
                                resultLI.appendChild(stationImage);
                                resultUL.appendChild(resultLI);

                            });

                            const resultEndLbl = document.createElement('p');
                            resultEndLbl.textContent = "End";

                            resultsElement.appendChild(resultStartLbl);
                            resultsElement.appendChild(resultUL);
                            resultsElement.appendChild(resultEndLbl);

                            //analysis section
                            const analysisElement = document.getElementById('analysis');
                            analysisElement.innerHTML = '';

                            const analysisLbl = document.createElement('h1');
                            analysisLbl.textContent = 'Analysis';
                            analysisLbl.style.textAlign = 'center';

                            const analysisTotalTime = document.createElement('h6');
                            analysisTotalTime.textContent = `Total journey duration: ${data.duration + ' min'}`;

                            const analysisTimeComplex = document.createElement('h6');
                            analysisTimeComplex.textContent = `Time complexity: ${fetchTimeComplexity(algorithm)}`;

                            const analysisExecutionTime = document.createElement('h6');
                            analysisExecutionTime.textContent = `Execution time: ${data.timeExecution.toFixed(6) + ' second'}`;

                            const analysisOptimalAlgo = document.createElement('h6');
                            analysisOptimalAlgo.textContent = `suggested algorithm: ${getMostOptimalAlgorithm(fromBoxValue, toBoxValue)}`;

                            analysisElement.appendChild(analysisLbl);
                            analysisElement.appendChild(document.createElement('br'));
                            analysisElement.appendChild(analysisTotalTime);
                            analysisElement.appendChild(document.createElement('br'));
                            analysisElement.appendChild(analysisTimeComplex);
                            analysisElement.appendChild(document.createElement('br'));
                            analysisElement.appendChild(analysisExecutionTime);
                            analysisElement.appendChild(document.createElement('br'));
                            analysisElement.appendChild(analysisOptimalAlgo);

                        } else {
                            document.getElementById('style-1').innerHTML += '<div>No route found.</div>';
                            document.getElementById('analysis').innerHTML += '<div>No route found.</div>';
                        }
                    })
                    .catch(error => {
                        document.getElementById('style-1').innerHTML = '';
                        document.getElementById('style-1').innerHTML = 'Error: ' + error.message;
                        document.getElementById('analysis').innerHTML = '';
                        document.getElementById('analysis').innerHTML = 'Error: ' + error.message;
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
        datalist.innerHTML = '';

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
                circle.setAttribute('fill', 'black');
            }
        });
    }

    //Reset all circles to no fill
    function resetPath() {
        circles.forEach(circle => {
            circle.setAttribute('fill', '');
        });
    }

    //get live crowd data from LTADataMall
    async function fetchLiveCrowdData() {
        const MRTLines = ['NSL', 'CCL', 'CEL', 'CGL', 'DTL', 'EWL', 'NEL', 'BPL', 'SLRT', 'PLRT'];

        //for each line the data is collect, push it into the main array.
        for (const line of MRTLines) {
            try {
                const response = await fetch(`/api/liveCrowdDensity?TrainLine=${line}`);
                if (!response.ok) {
                    throw new Error(`Failed to collect ${line}`);
                }
                const data = await response.json();
                if (data && Array.isArray(data.value)) {
                    combinedData.push(...data.value);
                } else {
                    console.error(`Data for ${line} is not in expected format`, data);
                }
            } catch (error) {
                console.error('Error fetching live crowd data:', error);
            }
        }
    }

    //use .find javascript function to get the data
    function getCrowdDensityLevel(MRTcode) {
        const stationData = combinedData.find(content => content.Station === MRTcode);
        return stationData ? stationData.CrowdLevel : 'station not found';
    }

    //use .find javascript function to get route info in json file.
    function searchRouteInfo(stationA, stationB) {
        const routeInfo = routeData[0].routes.find(content => (content.from.trim().toLowerCase() === stationA && content.to.trim().toLowerCase() === stationB) || (content.from.trim().toLowerCase() === stationB && content.to.trim().toLowerCase() === stationA));
        return routeInfo;
    }

    // function to filter string that remains alphabet
    function filterCharacter(stationCode) {
        return stationCode.replace(/[^a-zA-Z]/g, '');
    }

    // function used to return string thats used to call "image name"
    function stationLine(initial) {
        if (initial == 'TE') {
            return "Thomson–East Coast Line";
        }
        else if (initial == "NS") {
            return "North-South Line";
        }
        else if (initial == "EW" || initial == "CG") {
            return "East-West Line";
        }
        else if (initial == "CC") {
            return "Circle Line";
        }
        else if (initial == "DT") {
            return "Downtown Line";
        }
        else if (initial == "NE") {
            return "North-East line";
        }
        else if (initial == "PE" || initial == "PW" || initial == "PTC") {
            return "Punggol LRT";
        }
        else if (initial == "SE" || initial == "SW" || initial == "STC") {
            return "Sengkang LRT";
        }
        else if (initial == "BP") {
            return "Bukit Panjang LRT";
        }
    }

    //function used to return string thats used to call "icon name"
    function StationIcon(stationName) {
        if (stationName == 'Thomson East Coast Line') {
            return "TEL";
        }
        else if (stationName == "North South Line") {
            return "NSL";
        }
        else if (stationName == "East West Line" || stationName == "Changi Airport Line") {
            return "EWL";
        }
        else if (stationName == "Circle Line") {
            return "CCL";
        }
        else if (stationName == "Downtown Line") {
            return "DTL";
        }
        else if (stationName == "North East Line") {
            return "NEL";
        }

        else if (stationName == "Punggol LRT") {
            return "PLRT";
        }
        else if (stationName == "Sengkang LRT") {
            return "SLRT";
        }
        else if (stationName == "Bukit Panjang LRT") {
            return "BPLRT";
        }
    }

    //function used for calling all data in route.json file and store in a global array.
    async function fetchRouteInfo() {
        fetch('static/route.json')
            .then(response => response.json())
            .then(data => {
                routeData.push(data);
            })
            .catch(error => console.error('Error fetching JSON:', error));
    }

    // function to fetch and display the time complexity of the selected algorithm
    function fetchTimeComplexity(algorithm) {
        //Time complexitiy is pre-determined
        const timeComplexities = {
            'dfs': 'O(V + E)',
            'astar': 'O(E)',
            'bidirectional_astar': 'O(E)',
            'djikstras': 'O(E + V log V)',
            'bfs': 'O(V + E)',
            'bidirectional_bfs': 'O(V + E)',
            'bellmanford': 'O(VE)',
            'floyd': 'O(V^3)'
        };

        // get the time complexity for the selected algorithm
        const complexity = timeComplexities[algorithm] || 'Unknown';
        return complexity;
    }

    function getMostOptimalAlgorithm(fromBoxValue, toBoxValue) {
        const algoList = ['dfs', 'astar', 'bidirectional_astar', 'djikstras', 'bfs', 'bidirectional_bfs', 'bellmanford', 'floyd'];
        let currentSmallestDuration = Infinity;
        let currentSmallestTimeEx = Infinity;
        let optimalAlgorithm = null;

        algoList.forEach(algo => {
            const request = new XMLHttpRequest();
            request.open('GET', `/api/${algo}/?start=${fromBoxValue}&end=${toBoxValue}`, false); // `false` makes the request synchronous
            request.send(null);

            if (request.status === 200) {
                const data = JSON.parse(request.responseText);
                const duration = data.duration;
                const timeExecution = data.timeExecution;

                if (duration < currentSmallestDuration) {
                    currentSmallestDuration = duration;
                    optimalAlgorithm = algo;
                    currentSmallestTimeEx = timeExecution;
                } else if (duration === currentSmallestDuration && timeExecution < currentSmallestTimeEx) {
                    currentSmallestDuration = duration;
                    optimalAlgorithm = algo;
                    currentSmallestTimeEx = timeExecution;
                }
            } else {
                console.error('An error occurred:', request.statusText);
            }
        });

        if (optimalAlgorithm === 'dfs') {
            return 'DFS';
        }
        else if (optimalAlgorithm === 'astar') {
            return 'A Star';
        }
        else if (optimalAlgorithm === 'bidirectional_astar') {
            return 'Bidirectional A Star';
        }
        else if (optimalAlgorithm === 'djikstras') {
            return 'Djikstras';
        }
        else if (optimalAlgorithm === 'bfs') {
            return 'BFS';
        }
        else if (optimalAlgorithm === 'bidirectional_bfs') {
            return 'Bidirectional BFS';
        }
        else if (optimalAlgorithm === 'bellmanford') {
            return 'Bellman Ford';
        }
        else if (optimalAlgorithm === 'floyd') {
            return 'Floyd Warshall';
        }
    }

    // auto reload webpage every 30min.
    setInterval(function () {
        location.reload();
    }, 1800000);
});

