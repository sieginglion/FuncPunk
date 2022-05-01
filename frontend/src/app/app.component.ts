import { environment } from 'src/environments/environment';

import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { MatSelectionListChange } from '@angular/material/list';

type Func = {
  name: string;
  code: string;
};

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  constructor(private http: HttpClient) {}

  backendUrl: string = environment.backendUrl;
  funcs: Func[] = [
    {
      name: 'a',
      code: "print('a')\n",
    },
    {
      name: 'b',
      code: "print('b')\n",
    },
  ];
  defaultFunc: Func = {
    name: 'hello_world',
    code: `def main(request):\n    return 'Hello, World!'\n`,
  };
  selectedFunc: Func | null = null;

  ngOnInit(): void {
    // this.http
    //   .get(environment.backendUrl + '/func')
    //   .subscribe((data) => console.log(data));
  }

  selectFunc(e: MatSelectionListChange): void {
    this.selectedFunc = e.options[0].value;
  }

  addFunc(): void {
    this.selectedFunc = {
      name: 'hello_world',
      code: `def main(request):\n    return 'Hello, World!'\n`,
    };
    this.funcs.push(this.selectedFunc);
  }

  deploy(): void {
    this.http
      .put(
        `${this.backendUrl}/func/${this.selectedFunc.name}`,
        this.selectedFunc.code
      )
      .subscribe((data) => console.log(data));
  }
}
