from emoji import emojize


class Library:
    def __init__(self):
        self.books = []

    def add_book(self, title, author):
        """
        Add a book to the library with a title and author.

        Args:
            title (str): The title of the book. Cannot be empty.
            author (str): The author of the book. Cannot be empty.

        Examples:
            >> library = Library()
            >> library.add_book("1984", "George Orwell")
            📖 Adding new book...
            Book '1984' by 'George Orwell' added to the library.

        """

        print(f"{emojize(':open_book:')} Add New Book...")
        if not title or not author:
            print(
                f"{emojize(':cross_mark:')} ! FOR ADDING A BOOK YOU HAVE TO ENTER TITLE, AUTHOR."
            )
            print()
            return

        book = {"title": title, "author": author}
        self.books.append(book)
        print(
            f"{emojize(':check_mark_button:')} Book '{title}' Writer '{author}' added to the library"
        )
        print()

    def remove_book(self, title):
        """
        Remove a book from the library by its title (case-insensitive).

        Args:
            title (str): The title of the book to remove. Cannot be empty.

        Examples:
            >> library = Library()
            >> library.add_book("1984", "George Orwell")
            >> library.remove_book("1984")
            🗑️ Removing book...
            ✔ Book '1984' by 'George Orwell' removed from the library.
        """

        print(f"{emojize(':wastebasket:')} Removing book...")
        if not title:
            print(
                f"{emojize(':cross_mark:')} FOR REMOVING A BOOK, YOU CANNOT ENTERING EMPTY!"
            )
            print()
            return

        for book in self.books:
            if book["title"].lower() == title.lower():
                self.books.remove(book)
                print(
                    f"{emojize(':check_mark:')} '{book['title']}' by '{book['author']}' removed from the library."
                )
                print()
                return
        print(f"{emojize(':cross_mark:')} '{title}' FOR REMOVING NOT FOUNDED")
        print()

    def search_book(self, title):
        """
        Search for a book by its title (case-insensitive).

        Args:
            title (str): The title of the book to search for. Cannot be empty.

        Examples:
            >> library = Library()
            >> library.add_book("1984", "George Orwell")
            >> library.search_book("1984")
            🔍 Searching for book...
            Book '1984' by 'George Orwell' found in the library.
        """

        print(f"{emojize(':eyes:')} Searching for book...")
        if not title:
            print(
                f"{emojize(':cross_mark:')} FOR SEARCHING A BOOK, YOU CANNOT ENTERING EMPTY!"
            )
            print()
            return
        for book in self.books:
            if book["title"].lower() == title.lower():
                print(f"'{book['title']}' by '{book['author']}' found in the library.")
                print()
                return
        print(f"{emojize(':cross_mark:')} '{title}' BOOK NOT FOUNDED")
        print()

    def show_books(self):
        """
        Display all books in the library.

        If the library is empty, a message indicating this is shown.

        Examples:
            >> library = Library()
            >> library.add_book("1984", "George Orwell")
            >> library.show_books()
            📚📚 Books in the Library 📚📚
            📖 Book: '1984' by 'George Orwell'
        """

        if not self.books:
            print(f"{emojize(':open_file_folder:')} Library is empty")
            print()
            return

        print(
            f"{emojize(':books:')}{emojize(':books:')}List of the books on the library{emojize(':books:')}{emojize(':books:')}"
        )
        for book in self.books:
            print(
                f"{emojize(':open_book:')} Book: '{book['title']}' by '{book['author']}'"
            )


# Prevent direct execution and provide example usage for testing
if __name__ == "__main__":
    """Test the Library class with example usage."""
    library = Library()
    library.add_book("The Great Gatsby", "F. Scott Fitzgerald")
    library.add_book("1984", "George Orwell")
    library.show_books()
    library.search_book("1984")
    library.remove_book("The Great Gatsby")
    library.show_books()
