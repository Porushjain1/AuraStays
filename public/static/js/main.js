document.addEventListener('DOMContentLoaded', () => {
  // 1. Dynamic Scroll Navbar
  const navbar = document.querySelector('.navbar');
  
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        navbar.classList.add('navbar-scrolled');
      } else {
        navbar.classList.remove('navbar-scrolled');
      }
    });
  }

  // 2. Smooth Scroll Animations (Intersection Observer)
  const fadeElements = document.querySelectorAll('.fade-up-element');
  
  const fadeObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  });

  fadeElements.forEach(el => fadeObserver.observe(el));

  // 3. AJAX Filtering (Search & Destinations)
  window.fetchHotels = function(url) {
    const hotelGrid = document.getElementById('hotel-grid');
    if (!hotelGrid) return;
    
    // Show loading state
    hotelGrid.style.opacity = '0.3';
    
    fetch(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.text())
    .then(html => {
      hotelGrid.innerHTML = html;
      hotelGrid.style.opacity = '1';
      
      // Update URL without page reload
      window.history.pushState({path: url}, '', url);
      
      // Re-observe new elements for fade-up animation
      const newFadeElements = document.querySelectorAll('.fade-up-element');
      newFadeElements.forEach(el => {
        el.classList.remove('visible'); // ensure they start hidden
        fadeObserver.observe(el);
      });
    })
    .catch(err => {
      console.error('Error fetching hotels:', err);
      hotelGrid.style.opacity = '1';
    });
  };

  const searchForm = document.getElementById('search-form');
  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault(); // Stop normal submission
      
      const formData = new FormData(searchForm);
      const queryString = new URLSearchParams(formData).toString();
      const url = `/?${queryString}`;
      
      const searchBtn = searchForm.querySelector('button[type="submit"]');
      const originalBtnText = searchBtn.innerHTML;
      searchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
      searchBtn.disabled = true;
      
      fetchHotels(url);
      
      // Reset button after a short delay to indicate completion
      setTimeout(() => {
        searchBtn.innerHTML = originalBtnText;
        searchBtn.disabled = false;
      }, 500);
    });
  }

  // 4. Date Picker Validation
  const checkinInput = document.getElementById('checkin');
  const checkoutInput = document.getElementById('checkout');

  if (checkinInput && checkoutInput) {
    // Disable past dates
    const today = new Date().toISOString().split('T')[0];
    checkinInput.setAttribute('min', today);
    checkoutInput.setAttribute('min', today);

    checkinInput.addEventListener('change', function() {
      // Ensure checkout is always strictly after checkin
      if (this.value) {
        let checkinDate = new Date(this.value);
        checkinDate.setDate(checkinDate.getDate() + 1); // Next day
        let minCheckout = checkinDate.toISOString().split('T')[0];
        
        checkoutInput.setAttribute('min', minCheckout);
        
        // If current checkout is before new min checkout, update it
        if (checkoutInput.value && checkoutInput.value <= this.value) {
          checkoutInput.value = minCheckout;
        }
      }
    });
  }
});
