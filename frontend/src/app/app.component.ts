import { environment } from 'src/environments/environment';

import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { MatSelectionListChange } from '@angular/material/list';
import { MatSnackBar } from '@angular/material/snack-bar';

type Func = {
  name: string;
  code: string;
  running: boolean;
};

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  constructor(private http: HttpClient, private _snackBar: MatSnackBar) {}

  backendUrl = environment.backendUrl;
  funcs: Func[];
  selectedFunc: Func | null = null;

  ngOnInit(): void {
    this.http.get(this.backendUrl + '/funcs').subscribe((body: any) => {
      this.funcs = body.map((func: Func) => ({ ...func, running: true }));
    });
  }

  addFunc(): void {
    this.funcs.push({
      name: `func-${
        Math.max(
          ...this.funcs
            .filter((func) => func.name.match(/^func-[\d]+$/))
            .map((func) => parseInt(func.name.slice(5)))
        ) + 1
      }`,
      code: `def main(request):\n    return 'Hello, World!'\n`,
      running: false,
    });
  }

  selectFunc(e: MatSelectionListChange): void {
    this.selectedFunc = e.options[0].value;
  }

  deployFunc(): void {
    if (
      this.funcs.some(
        (func) => func.running && func.name == this.selectedFunc.name
      )
    ) {
      this._snackBar.open(`${this.selectedFunc.name} already exists`, null, {
        duration: 5000,
      });
    } else {
      this.http
        .put(
          `${this.backendUrl}/funcs/${this.selectedFunc.name}`,
          this.selectedFunc.code
        )
        .subscribe();
      for (let i = 0; i < this.funcs.length; i++) {
        if (this.funcs[i].name == this.selectedFunc.name) {
          this.funcs[i].running = true;
          break;
        }
      }
    }
  }

  deleteFunc(): void {
    if (this.selectedFunc.running) {
      this.http
        .delete(`${this.backendUrl}/funcs/${this.selectedFunc.name}`)
        .subscribe();
    }
    for (let i = 0; i < this.funcs.length; i++) {
      if (this.funcs[i].name == this.selectedFunc.name) {
        this.funcs.splice(i, 1);
        break;
      }
    }
  }
}
