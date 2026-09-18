
import base64
css_content = b'''
/* ======================================================================= */
/* 6. Dashboard Cards Content (Zebra Striping & Hover)                     */
/* ======================================================================= */
.content-wrapper .card-body table tbody tr:nth-child(odd),
.content-wrapper .card-body .nav-pills .nav-item:nth-child(odd) {
    background-color: #ffffff !important;
}

.content-wrapper .card-body table tbody tr:nth-child(even),
.content-wrapper .card-body .nav-pills .nav-item:nth-child(even) {
    background-color: #f8fafc !important;
}

.content-wrapper .card-body table tbody tr,
.content-wrapper .card-body .nav-pills .nav-item {
    transition: background-color 0.2s ease !important;
    color: #334155 !important;
}

.content-wrapper .card-body table tbody tr:hover,
.content-wrapper .card-body .nav-pills .nav-item:hover {
    background-color: #f1f5f9 !important;
}

.content-wrapper .card-body table tbody tr td,
.content-wrapper .card-body table tbody tr th {
    color: #334155 !important;
}

/* ======================================================================= */
/* 7. Top Navbar Links (Button-like & Active State)                        */
/* ======================================================================= */
.main-header .navbar-nav .nav-item > .nav-link {
    border-radius: 8px !important;
    margin: 0 4px !important;
    color: #475569 !important;
    transition: all 0.2s ease !important;
    font-weight: 600 !important;
    padding: 8px 12px !important;
}

/* Hover State (Inactive Links) */
.main-header .navbar-nav .nav-item > .nav-link:not(.active):not(.dropdown-toggle):hover,
.main-header .navbar-nav .nav-item > .nav-link:not(.active):hover {
    background-color: #e0f2fe !important;
    color: #0369a1 !important;
}

/* Active State (Crucial) */
.main-header .navbar-nav .nav-item > .nav-link.active,
.main-header .navbar-nav .nav-item.active > .nav-link,
.main-header .navbar-nav .nav-item > .nav-link[style*="font-weight: bold"] /* Fallback for Jazzmin active items */ {
    background-color: #0ea5e9 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3) !important;
}
'''
with open('d:/housing/backend/static/css/jazzmin_custom.css', 'a', encoding='utf-8') as f:
    f.write(css_content.decode('utf-8'))

