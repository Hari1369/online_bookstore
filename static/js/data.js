/* data.js — seed catalog. In production this is GET /api/products/ */

const BASE_BOOKS = [
  { id: 1, title: "The Glass Orchard", author: "Nadia Ferrow", price: 16.99, isbn: "978-1-2345-6701-1", category: "fiction", color: "#3F6B62", description: "A family splinters and reforms across three summers in an orchard that seems to remember everything." },
  { id: 2, title: "Salt for the Tide", author: "Marcus Ilundain", price: 14.50, isbn: "978-1-2345-6702-8", category: "fiction", color: "#A9812F", description: "A retired lighthouse keeper is pulled back to the coast when a boat washes up carrying his own handwriting." },
  { id: 3, title: "Nine Doors North", author: "Priya Ashcombe", price: 18.25, isbn: "978-1-2345-6703-5", category: "fiction", color: "#6B4C6B", description: "A locked-room mystery that unfolds across nine apartments in a single Edinburgh stairwell." },
  { id: 4, title: "The Quiet Catalogue", author: "Renata Obi", price: 13.99, isbn: "978-1-2345-6704-2", category: "fiction", color: "#2E5266", description: "A librarian discovers that every book she reclassifies changes something small in the world outside." },
  { id: 5, title: "How Rivers Remember", author: "Dr. Lucía Pardo", price: 24.00, isbn: "978-1-2345-6801-9", category: "non-fiction", color: "#7A4A2B", description: "A field naturalist's account of three river systems and what their silt reveals about climate history." },
  { id: 6, title: "The Unfinished City", author: "Tomasz Wren", price: 21.50, isbn: "978-1-2345-6802-6", category: "non-fiction", color: "#455A64", description: "A walking history of urban planning failures and the neighborhoods that grew from them anyway." },
  { id: 7, title: "Working with Your Hands", author: "Esme Okafor", price: 19.99, isbn: "978-1-2345-6803-3", category: "non-fiction", color: "#8A6A24", description: "Essays on craft, repair, and attention, drawn from a decade spent in furniture-repair workshops." },
  { id: 8, title: "Letters to a Young Cartographer", author: "Halvard Skei", price: 17.75, isbn: "978-1-2345-6804-0", category: "non-fiction", color: "#556B4F", description: "A memoir in correspondence about mapmaking, error, and the limits of representing a coastline." },
  { id: 9, title: "Principles of Algebraic Topology", author: "Prof. Wei-Lin Tam", price: 64.00, isbn: "978-1-2345-6901-3", category: "academic", color: "#33475B", description: "A graduate-level text covering homotopy, homology, and cohomology with worked problem sets." },
  { id: 10, title: "Comparative Constitutional Law", author: "Prof. Henriette Voss", price: 58.50, isbn: "978-1-2345-6902-0", category: "academic", color: "#5C3B3B", description: "A survey of constitutional design across common-law and civil-law jurisdictions, third edition." },
  { id: 11, title: "Foundations of Cognitive Linguistics", author: "Dr. Samuel Achebe", price: 49.99, isbn: "978-1-2345-6903-7", category: "academic", color: "#3E5C4E", description: "An introductory text on embodied cognition and its influence on grammar and metaphor." },
  { id: 12, title: "Statistical Methods for Ecology", author: "Dr. Freya Lindqvist", price: 54.25, isbn: "978-1-2345-6904-4", category: "academic", color: "#6B5138", description: "Applied statistics for field ecologists, with R code examples and population-modelling case studies." }
];

const CATEGORY_LABELS = { fiction: "Fiction", "non-fiction": "Non-fiction", academic: "Academic" };

function initials(title) {
  return title.split(" ").filter(w => /[A-Za-z]/.test(w[0])).slice(0, 3).map(w => w[0]).join("");
}

function coverHTML(book, big) {
  return `<div class="cover" style="background:${book.color}">
    <span>${escapeHTML(book.title)}</span>
  </div>`;
}

function escapeHTML(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

function formatPrice(n) {
  return '$' + n.toFixed(2);
}
