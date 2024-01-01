async function add_deck() {
    // Retrieve deck_name from browser prompt
    let deck_name = prompt("Enter the name for the deck");
    deck_name = {name: deck_name};
    
    // POST deck_name to /add_deck endpoint 
    await fetch("/add_deck", {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(deck_name)
    })

    // Refresh page AFTER deck data has been posted
    location.reload();
    return false;
}

function change_card_state() {
    // Retrieve show/hide button element from html
    let button = document.querySelector('#card_state');
    // Retrieve card back text element from html
    let card_back = document.querySelector('#card_back')

    // If the button is currently in the show state (back is hidden)
    if (button.innerText == 'Show') {
        // Change button state to hide (back is shown)
        button.innerHTML = 'Hide';
        // Remove hidden class attribute from card back text (back is shown)
        card_back.classList.remove('hidden')
    }
    // If the button is currently in the hide state (back is shown)
    else {
        // Change button state to show (back is hidden)
        button.innerHTML = "Show";
        // Add hidden class attribute to card back text (back is hidden)
        card_back.classList.add('hidden')
    }
}