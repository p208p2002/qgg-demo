import './App.css'
import { useState } from 'react'
const axios = require('axios');

let API_URI = ''
if (!process.env.NODE_ENV || process.env.NODE_ENV === 'development') {
  // dev code
  API_URI = 'http://localhost:8000/generate'
} else {
  // production code
  API_URI = '/generate'
}

// example input
function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}
let exampleInputText1 ="Harry Potter is a series of seven fantasy novels written by British author J. K. Rowling. The novels chronicle the lives of a young wizard, Harry Potter, and his friends Hermione Granger and Ron Weasley, all of whom are students at Hogwarts School of Witchcraft and Wizardry. The main story arc concerns Harry's struggle against Lord Voldemort, a dark wizard who intends to become immortal, overthrow the wizard governing body known as the Ministry of Magic and subjugate all wizards and Muggles."
let exampleInputText2 = "Game of Thrones is an American fantasy drama television series created by David Benioff and D. B. Weiss for HBO. It is an adaptation of A Song of Ice and Fire, a series of fantasy novels by George R. R. Martin, the first of which is A Game of Thrones. The show was shot in the United Kingdom, Canada, Croatia, Iceland, Malta, Morocco, and Spain. It premiered on HBO in the United States on April 17, 2011, and concluded on May 19, 2019, with 73 episodes broadcast over eight seasons."
let exampleInputText3 = "Facebook is an American online social media and social networking service based in Menlo Park, California, and a flagship service of the namesake company Facebook, Inc. It was founded by Mark Zuckerberg, along with fellow Harvard College students and roommates Eduardo Saverin, Andrew McCollum, Dustin Moskovitz, and Chris Hughes. The founders of Facebook initially limited membership to Harvard students. Membership was expanded to Columbia, Stanford, and Yale before being expanded to the rest of the Ivy League, MIT, NYU, Boston University, then various other universities in the United States and Canada, and lastly high school students. Since 2006, anyone who claims to be at least 13 years old has been allowed to become a registered user of Facebook, though this may vary depending on local laws. The name comes from the face book directories often given to American university students."
let exampleInputTexts = [exampleInputText1,exampleInputText2,exampleInputText3]
let exampleInputText = exampleInputTexts[getRandomInt(exampleInputTexts.length)]

function App() {
  let [context, setContext] = useState('')
  let [questionGroupSize, setQuestionGroupSize] = useState(5)
  let [questionGroup, setQuestionGroup] = useState([])
  let [disableGenBtn,setDisableGenBtn] = useState(false)
  let [genBtnTitle,setGenBtnTitle] = useState('Generate')

  let genQuestionGroup = (context, question_group_size, candidate_pool_size) => {
    if(context===''){
      context = exampleInputText
    }
    console.log(context, question_group_size, candidate_pool_size)
    setQuestionGroup([])
    setDisableGenBtn(true)
    setGenBtnTitle('Generating...')
    axios.post(API_URI, {
      context,
      question_group_size,
      candidate_pool_size
    })
      .then(function (response) {
        let { question_group = [] } = response.data
        setQuestionGroup(question_group)
      })
      .catch(function (error) {
        console.log(error);
      })
      .then(()=>{
        setDisableGenBtn(false)
        setGenBtnTitle('Generate')
      })
  }

  return (
    <div className="App container">
      <h1 className="text-center mt-3 mb-3">Question Group Generator Demo</h1>
      {/* <div className="form-floating mb-2"> */}
        {/* context input */}
        <textarea          
          value={context}
          onChange={(e) => {
            setContext(e.target.value)
          }}
          className="form-control"
          placeholder={exampleInputText}
          style={{ height: 200 }}
          id="floatingTextarea">
        </textarea>
        {/* <label htmlFor="floatingTextarea">Context</label> */}
      {/* </div> */}

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
                <label htmlFor="inputQuestionGroupSize" className="col-sm-3 col-form-label">question group size</label>
                <div className="col-sm-9">
                  {/* inputQuestionGroupSize */}
                  <input
                    onChange={(e) => {
                      setQuestionGroupSize(e.target.value)
                      if (e.target.value > 10) {
                        setTimeout(() => {
                          setQuestionGroupSize(10)
                        }, 200);
                      }
                    }}
                    value={questionGroupSize}
                    type="number"
                    className="form-control"
                    id="inputQuestionGroupSize"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <button
        disabled={disableGenBtn}
        type="button"
        className="mt-2 btn btn-success w-100"
        onClick={() => genQuestionGroup(context, questionGroupSize, questionGroupSize * 2)}
      >
        {genBtnTitle}
      </button>
      <hr />

      {questionGroup.map((question,i) => {
        return (
          <div className="mb-1 row">
            <label htmlFor={`Q${i+1}.`} className="col-2 col-md-1 col-form-label">Q{i+1}.</label>
            <div className="col-10">
              <input type="text" readOnly className="form-control-plaintext" id={`Q${i+1}.`} value={question} />
            </div>
          </div>
        )
      })}

    </div>
  );
}

export default App;
