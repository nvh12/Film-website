const likeButton = document.getElementById('like');
const dislikeButton = document.getElementById('dislike');
const addButton = document.getElementById('add');

likeButton.addEventListener('click', function () {
    movieTitle = this.getAttribute('data-movie-title');
    id = this.getAttribute('data-movie-id');
    sendAction(movieTitle, 'like', id);
});
dislikeButton.addEventListener('click', function () {
    movieTitle = this.getAttribute('data-movie-title');
    id = this.getAttribute('data-movie-id');
    sendAction(movieTitle, 'dislike', id);
});
addButton.addEventListener('click', function () {
    movieTitle = this.getAttribute('data-movie-title');
    id = this.getAttribute('data-movie-id');
    sendAction(movieTitle, 'add', id);
});

function sendAction(movieTitle, action, id) {
    fetch(`/description/${movieTitle}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action, id: id })
    })
    .then(response => response.json())
    .then(data => {
        const reactionElement = document.getElementById(`movie-${id}-reactions`);
        reactionElement.textContent = `Likes: ${data.likes} | Dislikes: ${data.dislikes}`;
    })
    
}