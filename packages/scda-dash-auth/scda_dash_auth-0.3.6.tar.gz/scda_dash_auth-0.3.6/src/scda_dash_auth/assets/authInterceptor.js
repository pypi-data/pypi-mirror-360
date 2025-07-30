/*
  This script provides a global interceptor for all network requests made by the Dash app.
  Its purpose is to catch 401 Unauthorized errors from the server and perform an
  immediate, forceful client-side redirect, which prevents the app from getting
  stuck in a loop of background requests.
*/

(function() {
    // A flag to ensure the redirect logic only runs once per navigation attempt.
    let isRedirecting = false;

    // --- THE CRITICAL FIX for the "Back Button" issue ---
    // Listen for the 'pageshow' event, which fires every time the page becomes visible.
    // This includes initial loads and navigations from the back-forward cache.
    window.addEventListener('pageshow', function(event) {
        // The 'persisted' property is true if the page was loaded from the bfcache.
        // If so, we must reset our redirect flag to allow the app to function again.
        if (event.persisted) {
            console.log('SCDAAuth: Page loaded from cache, resetting redirect flag.');
            isRedirecting = false;
        }
    });


    // Store the original, native fetch function to avoid infinite loops.
    const originalFetch = window.fetch;

    // Override the global window.fetch function.
    window.fetch = function() {
        // If a redirect has already been initiated, block all subsequent
        // network requests to stop the flood and allow the redirect to complete.
        if (isRedirecting) {
            // Return a promise that never resolves to silently kill the request.
            return new Promise(() => {});
        }

        // Pass all arguments to the original fetch function.
        const fetchPromise = originalFetch.apply(this, arguments);

        // Return a new promise that wraps the original one.
        return new Promise((resolve, reject) => {
            fetchPromise.then(response => {
                // Check if the server responded with a 401 Unauthorized status.
                if (response.status === 401) {
                    const redirectUrl = response.headers.get('X-Redirect-URL');

                    if (redirectUrl && !isRedirecting) {
                        isRedirecting = true;
                        console.log('SCDAAuth: Intercepted 401. Redirecting to:', redirectUrl);
                        window.location.href = redirectUrl;

                        // "Swallow" this response by returning a non-resolving promise,
                        // which prevents Dash's renderer from processing it.
                        return new Promise(() => {});
                    }
                }

                // For all other successful responses, resolve the promise so Dash can handle them.
                resolve(response);

            }).catch(error => {
                // If the fetch itself fails, reject the promise.
                console.error('SCDAAuth Fetch Interceptor Error:', error);
                reject(error);
            });
        });
    };
})();
