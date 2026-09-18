function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('CTF フラグ提出')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function getSpreadsheet() {
  return SpreadsheetApp.getActiveSpreadsheet();
}

// フォームの問題選択肢を取得
function getQuestions() {
  const sheet = getSpreadsheet().getSheetByName('Answers');
  const data = sheet.getDataRange().getValues();
  const questions = [];
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === '') continue;
    questions.push({ id: data[i][0], title: data[i][1] });
  }
  return questions;
}

// フラグ判定（結果をLogシートに記録）
function checkFlag(name, questionId, submittedFlag) {
  const ss = getSpreadsheet();
  const answerSheet = ss.getSheetByName('Answers');
  const logSheet = ss.getSheetByName('Log');
  const data = answerSheet.getDataRange().getValues();

  let correctFlag = null;
  let title = '';
  for (let i = 1; i < data.length; i++) {
    if (String(data[i][0]).trim() === String(questionId).trim()) {
      title = data[i][1];
      correctFlag = String(data[i][2]).trim();
      break;
    }
  }

  if (correctFlag === null) {
    return { status: 'error', message: '問題が見つかりません' };
  }

  const normalizedInput = submittedFlag.trim();
  // 大文字小文字を区別しない場合は次の行を有効化:
  // const isCorrect = normalizedInput.toLowerCase() === correctFlag.toLowerCase();
  const isCorrect = normalizedInput === correctFlag;

  logSheet.appendRow([
    new Date(),
    name,
    questionId,
    normalizedInput,
    isCorrect
  ]);

  return {
    status: isCorrect ? 'correct' : 'incorrect',
    message: isCorrect ? '正解です！' : '不正解です。もう一度確認してください。',
    title: title
  };
}

// 指定した名前の進捗状況（全問題の正解/未正解）を返す
function getProgress(name) {
  const ss = getSpreadsheet();
  const answerSheet = ss.getSheetByName('Answers');
  const logSheet = ss.getSheetByName('Log');

  const answerData = answerSheet.getDataRange().getValues();
  const logData = logSheet.getDataRange().getValues();

  // その名前が正解済みの問題IDを集める
  const solvedIds = new Set();
  for (let i = 1; i < logData.length; i++) {
    if (String(logData[i][1]) === String(name) && logData[i][4] === true) {
      solvedIds.add(String(logData[i][2]));
    }
  }

  const progress = [];
  for (let i = 1; i < answerData.length; i++) {
    if (answerData[i][0] === '') continue;
    progress.push({
      id: answerData[i][0],
      title: answerData[i][1],
      solved: solvedIds.has(String(answerData[i][0]))
    });
  }
  return progress;
}
