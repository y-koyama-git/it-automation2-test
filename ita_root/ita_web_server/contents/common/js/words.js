////////////////////////////////////////////////////////////////////////////////////////////////////
//
//   Exastro IT Automation / words.js
//
//   -----------------------------------------------------------------------------------------------
//
//   Copyright 2022 NEC Corporation
//
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.
//
////////////////////////////////////////////////////////////////////////////////////////////////////

const WD = ( function() {

const ja = {
    // common.js
    COMMON: {
        sys_err: 'システムエラー',
    },
    // UI
    UI: {
        MainMenu: 'メインメニュー',
        MenuGroup: 'メニューグループ',
        Favorite: 'お気に入り',
        History: '履歴',
        WsChange: 'ワークスペース切替',
        RoleList: 'ロール一覧',
        MenuSearch: 'メニュー検索',
        List: '一覧',
        ChangeHistory: '変更履歴',
        AllDownload: '全件ダウンロード・ファイル一括登録',
        AllDownloadExcel: '全件ダウンロード（Excel）',
        AllDownloadExcelText: '登録している項目の一覧をエクセルシートでダウンロードします。',
        AllDownloadJson: '全件ダウンロード（JSON）',
        AllDownloadJsonText: '登録している項目の一覧をJSONでダウンロードします。',
        NewDownloadExcel: '新規登録用ダウンロード（Excel）',
        NewDownloadExcelText: '新規登録用のエクセルシートをダウンロードします。',
        ExcelUpload: 'ファイル一括登録（Excel）',
        ExcelUploadText: '全件ダウンロード・新規登録用ダウンロードでダウンロードしたエクセルシートを編集し、ここからアップロードすることで一括して追加・編集ができます。',
        JsonUpload: 'ファイル一括登録（JSON）',
        JsonUploadText: 'JSONファイルをここからアップロードすることで一括して追加・編集ができます。',
        JsonUploadErr: 'JSONの形式が正しくありません。',
        AllDownloadHistoryExcel: '変更履歴全件ダウンロード（Excel）',
        AllDownloadHistoryExcelText: '登録している項目一覧の変更履歴全件をエクセルシートでダウンロードします。',
        AllUploadStart: '一括登録開始',
        AllUploadCancel: 'キャンセル',
        AllUploadFileName: 'ファイルネーム',
        AllUploadFileSize: 'ファイルサイズ',
        AllUploadCount: '件数',
    },
    TABLE: {
        confirm: '表示推奨件数を超えていますが、表示してもよろしいですか?',
        limit: '表示可能件数の上限を超えました。',
        invalid: 'バリデーションエラーです。',
        insert: '登録',
        err_row: 'エラー列',
        err_details: 'エラー内容',
        register: '登録',
        update: '更新',
        discard: '廃止',
        restore: '復活'
    },
    CONDUCTOR: {
        edit: getMessage.FTE02133,
        view: getMessage.FTE02134,
        update: getMessage.FTE02135,
        confirmation: getMessage.FTE02136
    }
};

return ja;

}());