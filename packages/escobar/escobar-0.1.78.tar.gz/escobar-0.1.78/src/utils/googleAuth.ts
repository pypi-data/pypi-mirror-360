/**
 * Google Authentication utilities for Escobar
 */

// Type definitions for Google API
declare global {
    interface Window {
        gapi: {
            load: (api: string, callback: (() => void) | {
                callback: () => void;
                onerror: (error: Error) => void;
            }) => void;
            auth2: {
                init: (options: { client_id: string, scope: string }) => Promise<any>;
                getAuthInstance: () => {
                    signIn: () => Promise<{
                        getBasicProfile: () => {
                            getName: () => string;
                            getEmail: () => string;
                        };
                        getAuthResponse: () => {
                            id_token: string;
                        };
                    }>;
                };
            };
        };
    }
}

/**
 * Configuration for Google Auth
 */
export interface GoogleAuthConfig {
    clientId: string;
    scope?: string;
}

/**
 * Result of a successful Google Sign-In
 */
export interface GoogleSignInResult {
    idToken: string;
    name?: string;
    email?: string;
}

/**
 * Class to handle Google Authentication
 */
export class GoogleAuthService {
    private config: GoogleAuthConfig;
    private isInitialized: boolean = false;
    private initPromise: Promise<void> | null = null;

    /**
     * Create a new GoogleAuthService
     * @param config Configuration for Google Auth
     */
    constructor(config: GoogleAuthConfig) {
        this.config = {
            scope: 'profile email',
            ...config
        };
    }

    /**
     * Load the Google API script
     * @returns Promise that resolves when the script is loaded
     */
    private loadGoogleApi(): Promise<void> {
        return new Promise((resolve, reject) => {
            // Check if script is already loaded
            if (document.querySelector('script[src="https://apis.google.com/js/platform.js"]')) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://apis.google.com/js/platform.js';
            script.async = true;
            script.defer = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load Google API script'));
            document.body.appendChild(script);
        });
    }

    /**
     * Initialize Google Auth
     * @returns Promise that resolves when Google Auth is initialized
     */
    public async initialize(): Promise<void> {
        if (this.isInitialized) {
            return Promise.resolve();
        }

        if (this.initPromise) {
            return this.initPromise;
        }

        this.initPromise = new Promise<void>(async (resolve, reject) => {
            try {
                // Load Google API script
                await this.loadGoogleApi();

                // Initialize Google Auth
                await new Promise<void>((resolveAuth, rejectAuth) => {
                    window.gapi.load('auth2', {
                        callback: () => {
                            window.gapi.auth2.init({
                                client_id: this.config.clientId,
                                scope: this.config.scope
                            })
                                .then(() => {
                                    this.isInitialized = true;
                                    resolveAuth();
                                })
                                .catch(rejectAuth);
                        },
                        onerror: rejectAuth
                    });
                });

                resolve();
            } catch (error) {
                this.initPromise = null;
                reject(error);
            }
        });

        return this.initPromise;
    }

    /**
     * Sign in with Google
     * @returns Promise that resolves with the sign-in result
     */
    public async signIn(): Promise<GoogleSignInResult> {
        await this.initialize();

        const auth2 = window.gapi.auth2.getAuthInstance();
        const googleUser = await auth2.signIn();

        const authResponse = googleUser.getAuthResponse();
        const idToken = authResponse.id_token;

        // Get user profile information
        const profile = googleUser.getBasicProfile();
        const name = profile.getName();
        const email = profile.getEmail();

        return {
            idToken,
            name,
            email
        };
    }

    /**
     * Get an API key using Google Sign-In
     * @param apiEndpoint The endpoint to request an API key from
     * @returns Promise that resolves with the API key
     */
    public async getApiKey(apiEndpoint?: string): Promise<string> {
        try {
            const signInResult = await this.signIn();

            // If an API endpoint is provided, send the token to the server
            if (apiEndpoint) {
                const response = await fetch(apiEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        idToken: signInResult.idToken,
                        email: signInResult.email
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to get API key from server');
                }

                const data = await response.json();
                return data.apiKey;
            }

            // For demo/development purposes, generate a mock API key
            // In production, you should always use a server endpoint
            return 'goog_' + Math.random().toString(36).substring(2, 15);
        } catch (error) {
            console.error('Error getting API key:', error);
            throw error;
        }
    }
}

// Create and export a singleton instance with a default configuration
// You can override this in your application
export const googleAuth = new GoogleAuthService({
    clientId: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com'
});

/**
 * Simple function to get an API key with Google Sign-In
 * @param successCallback Callback function called with the API key on success
 * @param errorCallback Callback function called with the error on failure
 */
export function getApiKeyWithGoogle(
    successCallback: (apiKey: string) => void,
    errorCallback?: (error: Error) => void
): void {
    googleAuth.getApiKey()
        .then(successCallback)
        .catch(error => {
            if (errorCallback) {
                errorCallback(error);
            } else {
                console.error('Error getting API key with Google:', error);
            }
        });
}
