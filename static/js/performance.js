document.addEventListener("DOMContentLoaded", function () {

    fetch("/performance_data")
        .then(response => response.json())
        .then(data => {

            console.log(data); // Debug check

            const months = data.monthly_scores.map(item => item.month);
            const scores = data.monthly_scores.map(item => item.avg_percentage);
            const logins = data.login_counts.map(item => item.login_count);

            if (months.length === 0) {
                document.querySelector("#quizChart").innerHTML =
                    "<p style='color:#0b2f7a'>No quiz data available yet.</p>";
                return;
            }

            var options = {
                chart: {
                    type: 'line',
                    height: 350
                },
                series: [
                    {
                        name: "Average Score %",
                        data: scores
                    },
                    {
                        name: "Login Count",
                        data: logins
                    }
                ],
                xaxis: {
                    categories: months
                },
                stroke: {
                    curve: 'smooth',
                    width: 3
                },
                colors: ['#0b2f7a', '#f5e6c8'],
                markers: {
                    size: 5
                }
            };

            var chart = new ApexCharts(document.querySelector("#quizChart"), options);
            chart.render();
        })
        .catch(error => {
            console.error("Error loading chart:", error);
        });
});