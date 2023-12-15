async function add_deck() {
    let deck_name = prompt("Enter the name for the deck");
    deck_name = {name: deck_name};
    
    await fetch("/add_deck", {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(deck_name)
    })

    location.reload();
    return false;
}