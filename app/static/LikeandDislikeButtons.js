const likeButton = document.getElementById("like");
const dislikeButton = document.getElementById("dislike");

likeButton.addEventListener("click", () => {
  likeButton.classList.add("activedLikeandDislike");
  dislikeButton.classList.remove("activedLikeandDislike");
});

dislikeButton.addEventListener("click", () => {
  dislikeButton.classList.add("activedLikeandDislike");
  likeButton.classList.remove("activedLikeandDislike");
});
