# Library Management System Demo

A Flask + MySQL library management system demo project with modern UI built using Bootstrap 5.3.3.

## Project Structure

### HTML Pages Classification (by menu order)

#### 1. Home Page
- `home.html` - Display top 3 popular books

#### 2. Book Management
- `book_list.html` - Book list and search page
- `book_manage.html` - Book add/edit form page
- `book_detail.html` - Book detail page

#### 3. Loan Management
- `loan.html` - Loan page with borrower, book, and copy selection

#### 4. Borrower Management
- `borrower_list.html` - Borrower list and search page
- `borrower_manage.html` - Borrower add/edit form page

#### 5. Loans by Borrower
- `loan_by_borrower.html` - Loan records grouped by borrower

#### 6. Current Loans
- `loan_current.html` - Current loan records and search page

### Route Classification (by menu order)

#### 1. Home Page Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Display top 3 popular books |

#### 2. Book Management Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/book_list` | GET | First time entry, show empty list |
| `/book_search` | POST | Handle search requests |
| `/book_add` | GET | Add new book form |
| `/book_manage/<int:book_id>` | GET | Edit book form |
| `/book_save` | POST | Save new book |
| `/book_save/<int:book_id>` | POST | Update existing book |
| `/book/<int:book_id>` | GET | Book detail page |

#### 3. Loan Management Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/loan` | GET/POST | Loan main page and create loan |
| `/loan_select_book` | POST | Select book and display details |

#### 4. Borrower Management Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/borrower_list` | GET/POST | Borrower list and search (shared route) |
| `/borrower_manage` | GET | Add new borrower form |
| `/borrower_manage/<int:borrower_id>` | GET | Edit borrower form |
| `/borrower_save` | POST | Save new borrower |
| `/borrower_save/<int:borrower_id>` | POST | Update existing borrower |

#### 5. Loans by Borrower Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/loan_by_borrower` | GET | Loan records grouped by borrower |
| `/return_book/<int:loan_id>` | POST | Return book |

#### 6. Current Loans Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/loan_current` | GET/POST | Current loan records and search |

## Technical Implementation Comparison

### Book Management vs Borrower Management Route Implementation Comparison

Book management and borrower management have similar functionality but use different implementation approaches. Book management uses one separate route per request, totaling 7 routes, while borrower management with similar functionality attempts to merge and share routes as much as possible, using only 3 routes in total.

### Form Validation Comparison

Book editing uses HTML's default validation mode for user input validation, while borrower management uses Bootstrap's built-in user input validation mode. Additionally, to maintain a consistent validation message display style, borrower editing uses regular expressions for user input validation.

#### Book Edit - HTML5 Default Validation
```html
<!-- Simple HTML5 validation with browser popup alerts -->
<input type="text" name="booktitle" required maxlength="45">
<input type="number" name="yearofpublication" min="1000" max="2099">
```

#### Borrower Edit - Bootstrap invalid-feedback Validation
```html
<!-- Bootstrap style validation with in-page error messages -->
<input type="text" name="firstname" required pattern="^[A-Za-z]{2,45}$">
<div class="invalid-feedback">
    Please provide a valid first name (2-45 letters only).
</div>
```

### List Books vs Loan by Borrower Query Comparison

List books does not perform queries on initial entry, while loan_by_borrower performs default queries after loading.

### Overdue Display Comparison

Loan_by_borrower uses table row background color to display overdue records, while current loan uses special overdue badges for display.

### Book Cover Image Size Control
The project uses custom CSS in `static/styles.css` to control book cover image dimensions:

```css
/* Home page popular books cover */
.book-cover-image {
    width: 120px;
    height: 160px;
    object-fit: cover;
}

/* Book detail page cover */
.book-detail-cover-image {
    width: 200px;
    height: 280px;
    object-fit: cover;
}
```