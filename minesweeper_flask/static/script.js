const boardElement = document.getElementById('board');
let board = initialBoard;

// Dynamically set grid size
boardElement.style.gridTemplateColumns = `repeat(${board[0].length}, 40px)`;
boardElement.style.gridTemplateRows = `repeat(${board.length}, 40px)`;

function renderBoard() {
    boardElement.innerHTML = '';
    board.forEach((row, r) => {
        row.forEach((cell, c) => {
            const cellDiv = document.createElement('div');
            cellDiv.className = 'cell';
            cellDiv.dataset.row = r;
            cellDiv.dataset.col = c;

            if (cell === 'F') {
                cellDiv.classList.add('flagged');
            } else if (cell !== '#') {
                cellDiv.classList.add('revealed');
                if (cell === 'X') cellDiv.classList.add('mine');
                else if (!isNaN(cell)) cellDiv.dataset.val = cell;
            }

            // Left click
            cellDiv.addEventListener('click', () => {
                handleAction(r, c, 'left');
            });

            // Right click (flag)
            cellDiv.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                handleAction(r, c, 'right');
            });

            boardElement.appendChild(cellDiv);
        });
    });
}

function handleAction(row, col, button) {
    fetch('/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row, col, button })
    })
    .then(res => res.json())
    .then(data => {
        board = data.board;
        renderBoard();

        const statusImg = document.getElementById('status-img');
        const restartBtn = document.getElementById('restart-btn');

        if (data.game_over) {
            if (statusImg) {
                statusImg.style.display = 'block';

                if (data.lost) {
                    statusImg.src = "/static/img/lose.png";
                    statusImg.alt = "You hit a mine!";
                    statusImg.style.display = 'inline-block';
                } else if (data.won) {
                    statusImg.src = "/static/img/win.png";
                    statusImg.alt = "You won!";
                } else {
                    statusImg.src = "/static/img/gameover.png"; // optional fallback
                    statusImg.alt = "Game Over";
                    statusImg.style.display = "inline-block"; 
                }
            }

            if (restartBtn) {
                restartBtn.style.display = 'inline-block';
            }
        }
    });
}

// Initial render
renderBoard();
