document.addEventListener('DOMContentLoaded', function() {
    var backBtn = document.createElement('a');
    backBtn.href = '/admin/';
    backBtn.className = 'btn btn-danger btn-sm mx-2';
    backBtn.innerHTML = '<i class="fas fa-arrow-right mr-1"></i> ???? ????? ??????';
    backBtn.style.cssText = 'font-weight: bold; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); height: 35px; display: flex; align-items: center; justify-content: center;';
    var navbar = document.querySelector('.main-header .navbar-nav:first-child');
    if (navbar) {
        var li = document.createElement('li');
        li.className = 'nav-item d-none d-sm-inline-block';
        li.style.display = 'flex';
        li.style.alignItems = 'center';
        li.appendChild(backBtn);
        navbar.appendChild(li);
    }
});
