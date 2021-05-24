import './App.css'

function App() {
  return (
    <div className="App container">
      <h1 className="text-center mt-3 mb-3">Question Group Generator Demo</h1>
      <div className="form-floating mb-2">
        <textarea
          className="form-control"
          placeholder="Please place an context here"
          style={{ height: 200 }}
          id="floatingTextarea">
        </textarea>
        <label htmlFor="floatingTextarea">Context</label>
      </div>

      <div className="accordion" id="accordionExample">
        <div className="accordion-item">
          <h2 className="accordion-header" id="headingTwo">
            <button className="btn btn-sm btn-light w-100 collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
              Generation Setting
            </button>
          </h2>
          <div id="collapseTwo" className="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#accordionExample">
            <div className="accordion-body">

              <div className="mb-3 row">
                <label htmlFor="inputPassword" className="col-sm-3 col-form-label">question group size</label>
                <div className="col-sm-9">
                  <input type="password" className="form-control" id="inputPassword" />
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>

      <div className="mt-2 btn btn-success w-100">Generate</div>
      <hr />
      <div className="mb-3 row">
        <label htmlFor="staticEmail" className="col-2 col-md-1 col-form-label">Q1.</label>
        <div className="col-10">
          <input type="text" readOnly className="form-control-plaintext" id="staticEmail" value="email@example.com" />
        </div>
      </div>
      <div className="mb-3 row">
        <label htmlFor="staticEmail" className="col-2 col-md-1 col-form-label">Q2.</label>
        <div className="col-10">
          <input type="text" readOnly className="form-control-plaintext" id="staticEmail" value="email@example.com" />
        </div>
      </div>
    </div>
  );
}

export default App;
