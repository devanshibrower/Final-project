document.addEventListener("DOMContentLoaded", function () {
    // Function to get gradient colors for each genre
    function getGenreGradient(genre) {
        const gradients = {
            'rock': ['#E74848', '#4B0082'],
            'alternative rock': ['#E74848', '#4B0082'],
            'modern rock': ['#E74848', '#4B0082'],
            'indie rock': ['#E74848', '#4B0082'],
            'punk rock': ['#E74848', '#4B0082'],
            'art rock': ['#FF8E53', '#8E44AD'],
            'hip hop': ['#D6E009', '#00BCD4'],
            'alternative hip hop': ['#D6E009', '#00BCD4'],
            'experimental hip hop': ['#D6E009', '#00BCD4'],
            'industrial hip hop': ['#D6E009', '#00BCD4'],
            'rap': ['#D6E009', '#00BCD4'],
            'darksynth': ['#BB97BB', '#2C003E'],
            'house': ['#00B8D4', '#1A237E'],
            'filter house': ['#00B8D4', '#1A237E'],
            'deep house': ['#00B8D4', '#1A237E'],
            'electro house': ['#00B8D4', '#1A237E'],
            'progressive house': ['#00B8D4', '#1A237E'],
            'oxford indie': ['#3F51B5', '#9FA8DA'],
            'pop': ['#FFD700', '#FF69B4'],
            'new americana': ['#F4A460', '#8B4513'],
            'stomp and holler': ['#FFA726', '#D84315'],
            'rave': ['#8A2BE2', '#00FF7F'],
            'permanent wave': ['#00BFA5', '#32426A'],
            'melancholia': ['#78909C', '#3E2723'],
            'indie': ['#9370DB', '#4B0082'],
            'electronic': ['#00CED1', '#0000FF'],
            'r&b': ['#DA70D6', '#8B008B'],
            'country': ['#DAA520', '#B8860B'],
            'jazz': ['#4682B4', '#000080'],
            'classical': ['#DEB887', '#D2691E'],
            'reggae': ['#32CD32', '#006400'],
            'blues': ['#4169E1', '#00008B'],
            'metal': ['#C0C0C0', '#2F4F4F'],
            'folk': ['#CD853F', '#8B4513'],
            'latin': ['#FF4500', '#8B0000'],
            'punk': ['#FF1493', '#8B0000'],
            'soul': ['#FF69B4', '#8A2BE2'],
            'funk': ['#FF00FF', '#9400D3'],
            'dance': ['#00FFFF', '#1E90FF'],
            'alternative': ['#32CD32', '#006400'],
            'disco': ['#FF69B4', '#FF00FF']
        };

        const defaultGradient = ['#A9A9A9', '#696969'];
        const normalizedGenre = genre.toLowerCase().trim();

        // Check if the genre matches any predefined gradients
        for (const [key, value] of Object.entries(gradients)) {
            if (normalizedGenre.includes(key)) {
                return value;
            }
        }

        // Return default gradient if no match found
        return defaultGradient;
    }

    // Select all playlist items
    const playlistItems = document.querySelectorAll('#playlists li');
    
    // Function to handle playlist selection
    function selectPlaylist(playlistItem) {
        // Remove 'selected' class from all items
        playlistItems.forEach(item => item.classList.remove('selected'));
        // Add 'selected' class to the clicked item
        playlistItem.classList.add('selected');
        // Get the playlist ID and fetch its genre counts
        const playlistId = playlistItem.getAttribute('data-playlist-id');
        fetchGenreCounts(playlistId);
    }

    // Add click event listeners to all playlist items
    playlistItems.forEach(item => {
        item.addEventListener('click', function() {
            selectPlaylist(this);
        });
    });

    // Function to fetch genre counts from the server
    function fetchGenreCounts(playlistId) {
        fetch(`/get_genre_counts/${playlistId}`)
            .then(response => response.json())
            .then(data => {
                updateTreemap(data);
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to update the treemap visualization
    function updateTreemap(genreCounts) {
        // Clear existing chart
        d3.select("#chart").selectAll("*").remove();

        const width = document.getElementById('chart').clientWidth;
        const height = 600;

        // Prepare data for D3 hierarchy
        const data = {
            name: "Genres",
            children: Object.entries(genreCounts).map(([key, value]) => ({
                name: key,
                value: value
            }))
        };

        // Create D3 hierarchy and treemap layout
        const root = d3.hierarchy(data)
            .sum(d => d.value)
            .sort((a, b) => b.value - a.value);

        const treemap = d3.treemap()
            .size([width, height])
            .padding(1);

        treemap(root);

        // Create SVG element
        const svg = d3.select("#chart")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const defs = svg.append("defs");

        // Create nodes for each genre
        const nodes = svg.selectAll("g")
            .data(root.leaves())
            .enter()
            .append("g")
            .attr("transform", d => `translate(${d.x0},${d.y0})`);

        // Add rectangles and text for each node
        nodes.each(function(d) {
            const node = d3.select(this);
            const [color1, color2] = getGenreGradient(d.data.name);
            const gradientId = `gradient-${d.data.name.replace(/\s+/g, '-')}-${Math.random().toString(36).substr(2, 9)}`;

            // Create radial gradient for each genre
            const gradient = defs.append("radialGradient")
                .attr("id", gradientId)
                .attr("cx", "50%")
                .attr("cy", "50%")
                .attr("r", "60%")
                .attr("fx", "50%")
                .attr("fy", "50%");

            gradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", color1);

            gradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", color2);

            // Add rectangle for each genre
            node.append("rect")
                .attr("width", d.x1 - d.x0)
                .attr("height", d.y1 - d.y0)
                .attr("fill", `url(#${gradientId})`)
                .attr("stroke", "#fff")
                .attr("stroke-width", "1px");

            // Add text label for each genre
            node.append("text")
                .attr("x", 8)
                .attr("y", 15)
                .text(d.data.name)
                .attr("font-size", "12px")
                .attr("fill", "white")
                .attr("text-shadow", "1px 1px 2px rgba(0,0,0,0.5)");
        });
    }

    // Create initial treemap with data from the server
    const initialGenreCounts = JSON.parse(document.getElementById('initial-genre-counts').textContent);
    updateTreemap(initialGenreCounts);

    // Select the first playlist by default
    if (playlistItems.length > 0) {
        selectPlaylist(playlistItems[0]);
    }
});
