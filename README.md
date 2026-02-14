# Nixagone

Nixagone is a modern, customizable e-commerce web application built with Django. It features a clean UI, robust product management, cart and order handling, and is ready for deployment on platforms like PythonAnywhere.

---

## Features

- **Product Catalog**: Browse, search, and filter products by category.
- **Shopping Cart**: Add, update, and remove products from the cart.
- **Order Management**: Checkout process with delivery cost calculation.
- **Custom User Model**: Extensible user authentication.
- **Admin Dashboard**: Manage products, orders, and users.
- **Responsive Design**: Mobile-friendly UI using Tailwind CSS and Alpine.js.
- **SEO & Social**: Robots.txt, meta tags, and social links in the footer.
- **Environment-based Settings**: Uses `.env` for secrets and database configuration.

---

## Project Structure

```
apps/
  cart/         # Cart logic and models
  order/        # Order processing and checkout
  product/      # Product catalog and categories
main/           # Main app: users, forms, views, etc.
nix/            # Django project settings, URLs, WSGI/ASGI
static/         # CSS, JS (Tailwind, Alpine.js), images
templates/      # HTML templates (base, product, cart, order, admin, partials)
media/          # Uploaded product images
```

---

## Getting Started

### 1. Clone & Install

```sh
git clone https://github.com/ssshiponu/nixagone
cd nixagone
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the root:

```
SECRET_KEY=your-secret-key  #generate a secret key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # or your Postgres URL
```

### 3. Database & Static Files

```sh
python manage.py migrate
python manage.py collectstatic
```

### 4. Run the Server

```sh
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Customization

- **Site Title & Configs**: Set via Django admin or config tags in templates.
- **Styling**: Edit `static/css/main.css` and `tailwind.config.js`.
- **JS Interactivity**: Powered by Alpine.js (`static/js/alpine.js`).

---

## Deployment

- Set `DEBUG=False` and configure `ALLOWED_HOSTS` in `.env`.
- Use Postgres for production (`DATABASE_URL`).
- Configure static/media file serving as per your host.

---

## License

MIT License

---

## Credits

- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Alpine.js](https://alpinejs.dev/)

---

**Happy coding!**# Django_Shop_783827
