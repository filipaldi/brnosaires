// Shared validation error. Messages are user-facing (Slovak).

export class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
  }
}
