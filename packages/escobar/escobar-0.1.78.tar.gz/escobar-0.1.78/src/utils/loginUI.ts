import { getApiKeyWithGoogle } from './googleAuth';

/**
 * Interface for authentication provider options
 */
export interface IAuthProvider {
    id: string;
    name: string;
    icon: string;
    description: string;
}

/**
 * Class to manage the login UI
 */
export class LoginUI {
    private overlay: HTMLDivElement;
    private container: HTMLDivElement;
    private onSuccess: (apiKey: string) => void;
    private onCancel: () => void;

    // Available authentication providers (excluding email/password which is handled separately)
    private authProviders: IAuthProvider[] = [
        {
            id: 'google',
            name: 'Google',
            icon: '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>',
            description: 'Sign in with your Google account'
        },
        {
            id: 'microsoft',
            name: 'Microsoft',
            icon: '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="#f25022" d="M1 1h10v10H1V1z"/><path fill="#00a4ef" d="M1 13h10v10H1V13z"/><path fill="#7fba00" d="M13 1h10v10H13V1z"/><path fill="#ffb900" d="M13 13h10v10H13V13z"/></svg>',
            description: 'Sign in with your Microsoft account'
        },
        {
            id: 'github',
            name: 'GitHub',
            icon: '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="#24292e" d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>',
            description: 'Sign in with your GitHub account'
        },
        {
            id: 'okta',
            name: 'Okta',
            icon: '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="#007dc1" d="M12 0C5.389 0 0 5.389 0 12s5.389 12 12 12 12-5.389 12-12S18.611 0 12 0zm0 18c-3.314 0-6-2.686-6-6s2.686-6 6-6 6 2.686 6 6-2.686 6-6 6z"/></svg>',
            description: 'Sign in with your Okta account'
        }
    ];

    /**
     * Create a new LoginUI
     * @param onSuccess Callback when authentication is successful
     * @param onCancel Callback when authentication is cancelled
     */
    constructor(
        onSuccess: (apiKey: string) => void,
        onCancel: () => void
    ) {
        this.onSuccess = onSuccess;
        this.onCancel = onCancel;

        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'escobar-login-overlay';
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.hide();
                this.onCancel();
            }
        });

        // Create container
        this.container = this.createContainer();
        this.overlay.appendChild(this.container);
    }

    /**
     * Create the login UI container
     */
    private createContainer(): HTMLDivElement {
        // Create container
        const container = document.createElement('div');
        container.className = 'escobar-login-container';

        // Create header
        const header = document.createElement('div');
        header.className = 'escobar-login-header';

        const title = document.createElement('h2');
        title.textContent = 'Get API Key';
        header.appendChild(title);

        const closeButton = document.createElement('button');
        closeButton.className = 'escobar-login-close-button';
        closeButton.innerHTML = '&times;';
        closeButton.addEventListener('click', () => {
            this.hide();
            this.onCancel();
        });
        header.appendChild(closeButton);

        container.appendChild(header);

        // Create content
        const content = document.createElement('div');
        content.className = 'escobar-login-content';

        // Add email/password form
        const emailForm = document.createElement('form');
        emailForm.className = 'escobar-login-email-form';
        emailForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleEmailLogin(emailForm);
        });

        const emailLabel = document.createElement('label');
        emailLabel.textContent = 'Email';
        emailLabel.htmlFor = 'escobar-login-email';
        emailForm.appendChild(emailLabel);

        const emailInput = document.createElement('input');
        emailInput.type = 'email';
        emailInput.id = 'escobar-login-email';
        emailInput.className = 'escobar-login-input';
        emailInput.placeholder = 'Enter your email';
        emailInput.required = true;
        emailForm.appendChild(emailInput);

        const passwordLabel = document.createElement('label');
        passwordLabel.textContent = 'Password';
        passwordLabel.htmlFor = 'escobar-login-password';
        emailForm.appendChild(passwordLabel);

        const passwordInput = document.createElement('input');
        passwordInput.type = 'password';
        passwordInput.id = 'escobar-login-password';
        passwordInput.className = 'escobar-login-input';
        passwordInput.placeholder = 'Enter your password';
        passwordInput.required = true;
        emailForm.appendChild(passwordInput);

        const emailSubmitButton = document.createElement('button');
        emailSubmitButton.type = 'submit';
        emailSubmitButton.className = 'escobar-login-email-button';
        emailSubmitButton.textContent = 'Login with Email';
        emailForm.appendChild(emailSubmitButton);

        content.appendChild(emailForm);

        // Add separator
        const separator = document.createElement('div');
        separator.className = 'escobar-login-separator';
        separator.innerHTML = '<span>OR</span>';
        content.appendChild(separator);

        // Add description for SSO options
        const description = document.createElement('p');
        description.className = 'escobar-login-description';
        description.textContent = 'Sign in with a provider:';
        content.appendChild(description);

        // Add auth providers
        const providersList = document.createElement('div');
        providersList.className = 'escobar-login-providers';

        this.authProviders.forEach(provider => {
            const providerButton = document.createElement('button');
            providerButton.className = 'escobar-login-provider-button';
            providerButton.dataset.provider = provider.id;

            const providerIcon = document.createElement('span');
            providerIcon.className = 'escobar-login-provider-icon';
            providerIcon.innerHTML = provider.icon;
            providerButton.appendChild(providerIcon);

            const providerInfo = document.createElement('div');
            providerInfo.className = 'escobar-login-provider-info';

            const providerName = document.createElement('div');
            providerName.className = 'escobar-login-provider-name';
            providerName.textContent = provider.name;
            providerInfo.appendChild(providerName);

            const providerDesc = document.createElement('div');
            providerDesc.className = 'escobar-login-provider-description';
            providerDesc.textContent = provider.description;
            providerInfo.appendChild(providerDesc);

            providerButton.appendChild(providerInfo);

            // Add click handler
            providerButton.addEventListener('click', () => {
                this.handleProviderClick(provider.id);
            });

            providersList.appendChild(providerButton);
        });

        content.appendChild(providersList);
        container.appendChild(content);

        return container;
    }

    /**
     * Handle provider button click
     */
    private handleProviderClick(providerId: string): void {
        // Currently only Google is implemented
        if (providerId === 'google') {
            // Show loading state
            this.setLoadingState(providerId, true);

            // Use the existing Google auth function
            getApiKeyWithGoogle(
                // Success callback
                (apiKey) => {
                    this.setLoadingState(providerId, false);
                    this.hide();
                    this.onSuccess(apiKey);
                },
                // Error callback
                (error) => {
                    console.error('Google Sign-In error:', error);
                    this.setLoadingState(providerId, false);
                    alert('Failed to sign in with Google. Please try again.');
                }
            );
        } else {
            // For other providers, just show a placeholder message
            alert(`${this.getProviderById(providerId).name} authentication is not yet implemented.`);
        }
    }

    /**
     * Handle email login form submission
     */
    private handleEmailLogin(form: HTMLFormElement): void {
        const emailInput = form.querySelector('#escobar-login-email') as HTMLInputElement;
        const passwordInput = form.querySelector('#escobar-login-password') as HTMLInputElement;
        const submitButton = form.querySelector('.escobar-login-email-button') as HTMLButtonElement;

        if (!emailInput || !passwordInput || !submitButton) {
            return;
        }

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            alert('Please enter both email and password');
            return;
        }

        // Show loading state
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';

        // Simulate API call with a timeout
        setTimeout(() => {
            // Generate a deterministic API key based on email
            // This uses a simple hash function to convert the email to a consistent key
            const apiKey = this.generateDeterministicKey(email);

            // Reset form
            submitButton.disabled = false;
            submitButton.textContent = 'Login with Email';

            // Hide the login UI and return the API key
            this.hide();
            this.onSuccess(apiKey);
        }, 1500);
    }

    /**
     * Set loading state for a provider button
     */
    private setLoadingState(providerId: string, isLoading: boolean): void {
        const button = this.container.querySelector(`button[data-provider="${providerId}"]`) as HTMLButtonElement;
        if (!button) return;

        if (isLoading) {
            button.disabled = true;
            button.classList.add('escobar-login-provider-loading');
            const providerName = button.querySelector('.escobar-login-provider-name');
            if (providerName) {
                providerName.textContent = `Connecting to ${this.getProviderById(providerId).name}...`;
            }
        } else {
            button.disabled = false;
            button.classList.remove('escobar-login-provider-loading');
            const providerName = button.querySelector('.escobar-login-provider-name');
            if (providerName) {
                providerName.textContent = this.getProviderById(providerId).name;
            }
        }
    }

    /**
     * Generate a deterministic API key based on email
     * This implements a simple hash function to create a consistent key for the same email
     */
    private generateDeterministicKey(email: string): string {
        // Simple hash function
        let hash = 0;
        for (let i = 0; i < email.length; i++) {
            const char = email.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }

        // Convert hash to a hex string and ensure it's positive
        const hashHex = Math.abs(hash).toString(16);

        // Add a prefix to indicate this is an email-based key
        return `email_${hashHex}`;
    }

    /**
     * Get provider by ID
     */
    private getProviderById(id: string): IAuthProvider {
        return this.authProviders.find(p => p.id === id) || this.authProviders[0];
    }

    /**
     * Show the login UI
     */
    public show(): void {
        document.body.appendChild(this.overlay);
        // Add animation class after a small delay to trigger animation
        setTimeout(() => {
            this.overlay.classList.add('escobar-login-overlay-visible');
            this.container.classList.add('escobar-login-container-visible');
        }, 10);
    }

    /**
     * Hide the login UI
     */
    public hide(): void {
        this.overlay.classList.remove('escobar-login-overlay-visible');
        this.container.classList.remove('escobar-login-container-visible');

        // Remove from DOM after animation completes
        setTimeout(() => {
            if (this.overlay.parentNode) {
                this.overlay.parentNode.removeChild(this.overlay);
            }
        }, 300); // Match the CSS transition duration
    }
}

/**
 * Show the login UI and return a promise that resolves with the API key
 */
export function showLoginUI(): Promise<string> {
    return new Promise((resolve, reject) => {
        const loginUI = new LoginUI(
            // Success callback
            (apiKey) => {
                resolve(apiKey);
            },
            // Cancel callback
            () => {
                reject(new Error('Authentication cancelled'));
            }
        );
        loginUI.show();
    });
}
