import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FEATURES, Feature } from './feature-schema';
import { PredictionService, PredictionResponse } from './prediction.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  readonly fields = FEATURES;
  readonly deployedStatic = !['localhost', '127.0.0.1']
    .includes(window.location.hostname);
  values: Record<string, string | number | null> = {};
  // signals: change detection works in BOTH zoneless (Angular 21+ default) and zone-based apps
  loading = signal(false);
  error = signal('');
  result = signal<PredictionResponse | null>(null);
  private api = inject(PredictionService);

  constructor() {
    for (const field of this.fields) this.values[field.name] = null;
  }

  trackField(_index: number, field: Feature) { return field.name; }

  pct(p: number): string { return (p * 100).toFixed(1) + '%'; }

  submit() {
    this.error.set(''); this.result.set(null);
    if (this.deployedStatic) {
      this.error.set('Static GitHub Pages demo: start Angular + Flask locally for predictions.');
      return;
    }
    const payload: Record<string, string | number> = {};
    for (const field of this.fields) {
      const value = this.values[field.name];
      if (value === null || value === '') {
        this.error.set(`Enter a value for ${field.label}`); return;
      }
      if (field.kind === 'number') {
        const numeric = Number(value);
        if (!Number.isFinite(numeric)) {
          this.error.set(`Invalid number for ${field.label}`); return;
        }
        if ((field.min !== undefined && numeric < field.min) ||
            (field.max !== undefined && numeric > field.max)) {
          this.error.set(`Out-of-range value for ${field.label} (${field.min}–${field.max})`); return;
        }
        payload[field.name] = numeric;
      } else {
        payload[field.name] = String(value);
      }
    }
    this.loading.set(true);
    this.api.predict(payload).subscribe({
      next: result => { this.result.set(result); this.loading.set(false); },
      error: err => {
        this.error.set(`API error ${err.status || ''}: ` +
          (err.error?.detail || err.error?.error || err.message || 'Check Flask terminal'));
        this.loading.set(false);
      },
    });
  }
}
