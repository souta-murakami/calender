import tkinter as tk
import tkinter.ttk as ttk
import datetime as da
import calendar as ca
import pymysql


WEEK = ['日', '月', '火', '水', '木', '金', '土']
WEEK_COLOUR = ['red', 'black', 'black', 'black','black', 'black', 'blue']
actions = ('学校','試験', '課題', '行事', '就活', 'アルバイト','旅行')

class Yic:
  def __init__(self, root):
    root.title('予定管理アプリ')
    root.geometry('520x280')
    root.resizable(0, 0)
    root.grid_columnconfigure((0, 1), weight=1)
    self.sub_win = None

    self.year  = da.date.today().year
    self.mon = da.date.today().month
    self.today = da.date.today().day

    self.title = None
    self.plan = None

    # ログインIDの記録
    # self.login_id = login_id
    # self.now_id = login_id

    # 左側のカレンダー部分
    leftFrame = tk.Frame(root)
    leftFrame.grid(row=0, column=0)
    self.leftBuild(leftFrame)

    # 右側の予定管理部分
    rightFrame = tk.Frame(root)
    rightFrame.grid(row=0, column=1)
    self.rightBuild(rightFrame)


  #-----------------------------------------------------------------
  # アプリの左側の領域を作成する
  #
  # leftFrame: 左側のフレーム
  def leftBuild(self, leftFrame):
    self.viewLabel = tk.Label(leftFrame, font=('', 10))
    beforButton = tk.Button(leftFrame, text='＜', font=('', 10), command=lambda:self.disp(-1))
    nextButton = tk.Button(leftFrame, text='＞', font=('', 10), command=lambda:self.disp(1))

    self.viewLabel.grid(row=0, column=1, pady=10, padx=10)
    beforButton.grid(row=0, column=0, pady=10, padx=10)
    nextButton.grid(row=0, column=2, pady=10, padx=10)

    self.calendar = tk.Frame(leftFrame)
    self.calendar.grid(row=1, column=0, columnspan=3)
    self.disp(0)


  #-----------------------------------------------------------------
  # アプリの右側の領域を作成する
  #
  # rightFrame: 右側のフレーム
  def rightBuild(self, rightFrame):
    r1_frame = tk.Frame(rightFrame)
    r1_frame.grid(row=0, column=0, pady=10)

    temp = '{}年{}月{}日の予定'.format(self.year, self.mon, self.today)
    self.title = tk.Label(r1_frame, text=temp, font=('', 12))
    self.title.grid(row=0, column=0, padx=20)

    button = tk.Button(rightFrame, text='追加', command=lambda:self.add())
    button.grid(row=0, column=1)

    self.r2_frame = tk.Frame(rightFrame)
    self.r2_frame.grid(row=1, column=0)

    self.schedule()


  #-----------------------------------------------------------------
  # アプリの右側の領域に予定を表示する
  #
  def schedule(self):
    # ウィジットを廃棄
    for widget in self.r2_frame.winfo_children():
      widget.destroy()

    # データベースに予定の問い合わせを行う


    
    temp = self.getplan()

 
    print(temp)
    # 表示方法を記載
    if not temp:
      temp = ""
      self.ttd = tk.Label(self.r2_frame, text=temp, font=('', 12))
      self.ttd.grid(row=1, column=1, padx=0)
  
    else:
      for idx in range(len(temp)):
        print(temp[idx])
        self.ttd = tk.Label(self.r2_frame, text=temp[idx], font=("", 12))
        self.ttd.grid(row=idx+1, column=0, padx=0)


  def getplan(self):

    # トランザクションの開始
    connection = pymysql.connect(host='127.0.0.1',
                               user='root',
                               password='',
                               db='apr01',
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

    try:

        connection.begin()

        with connection.cursor() as cursor:

          cursor = connection.cursor()

          # データの取得
          data = "SELECT kinds, memo FROM schedule WHERE days = '{}-{}-{}';".format(self.year, self.mon, self.today)
          print(self.year, self.mon, self.today) # 日付をプロンプトに表示
        cursor.execute(data)
        results = cursor.fetchall() # 入っているデータを表示
        print(results)
        datalist = [] # displayという空のリストを作成

        if len(results) != 0:
          for i in range(len(results)):
            kinds = results[i]["kinds"]
            memo = results[i]["memo"]
            data = "{}:{}".format(kinds, memo)
            datalist.append(data) # datalistに要素の追加

        return datalist

        connection.commit()

        #print('n'.join(results))
        #for r in results:
        #  print(r['kinds'], r['memo'])


    except Exception as e:
        print("error:", e)
        connection.rollback()
    finally:
        connection.close()


  #-----------------------------------------------------------------
  # カレンダーを表示する
  #
  # argv: -1 = 前月
  #        0 = 今月（起動時のみ）
  #        1 = 次月
  def disp(self, argv):
    self.mon = self.mon + argv
    if self.mon < 1:
      self.mon, self.year = 12, self.year - 1
    elif self.mon > 12:
      self.mon, self.year = 1, self.year + 1

    self.viewLabel['text'] = '{}年{}月'.format(self.year, self.mon)

    cal = ca.Calendar(firstweekday=6)
    cal = cal.monthdayscalendar(self.year, self.mon)

    # ウィジットを廃棄
    for widget in self.calendar.winfo_children():
      widget.destroy()

    # 見出し行
    r = 0
    for i, x in enumerate(WEEK):
      label_day = tk.Label(self.calendar, text=x, font=('', 10), width=3, fg=WEEK_COLOUR[i])
      label_day.grid(row=r, column=i, pady=1)

    # カレンダー本体
    r = 1
    for week in cal:
      for i, day in enumerate(week):
        if day == 0: day = ' ' 
        label_day = tk.Label(self.calendar, text=day, font=('', 10), fg=WEEK_COLOUR[i], borderwidth=1)
        if (da.date.today().year, da.date.today().month, da.date.today().day) == (self.year, self.mon, day):
          label_day['relief'] = 'solid'
        label_day.bind('<Button-1>', self.click)
        label_day.grid(row=r, column=i, padx=2, pady=1)
      r = r + 1

    # 画面右側の表示を変更
    if self.title is not None:
      self.today = 1
      self.title['text'] = '{}年{}月{}日の予定'.format(self.year, self.mon, self.today)


  #-----------------------------------------------------------------
  # 予定を追加したときに呼び出されるメソッド
  #
  def add(self):
    if self.sub_win == None or not self.sub_win.winfo_exists():
      self.sub_win = tk.Toplevel()
      self.sub_win.geometry("300x300")
      self.sub_win.resizable(0, 0)

      # ラベル
      sb1_frame = tk.Frame(self.sub_win)
      sb1_frame.grid(row=0, column=0)
      temp = '{}年{}月{}日　追加する予定'.format(self.year, self.mon, self.today)
      title = tk.Label(sb1_frame, text=temp, font=('', 12))
      title.grid(row=0, column=0)

      # 予定種別（コンボボックス）
      sb2_frame = tk.Frame(self.sub_win)
      sb2_frame.grid(row=1, column=0)
      label_1 = tk.Label(sb2_frame, text='種別 :  ', font=('', 10))
      label_1.grid(row=0, column=0, sticky=tk.W)
      self.combo = ttk.Combobox(sb2_frame, state='readonly', values=actions)
      self.combo.current(0)
      self.combo.grid(row=0, column=1)

      # テキストエリア（垂直スクロール付）
      sb3_frame = tk.Frame(self.sub_win)
      sb3_frame.grid(row=2, column=0)
      self.text = tk.Text(sb3_frame, width=40, height=15)
      self.text.grid(row=0, column=0)
      scroll_v = tk.Scrollbar(sb3_frame, orient=tk.VERTICAL, command=self.text.yview)
      scroll_v.grid(row=0, column=1, sticky=tk.N+tk.S)
      self.text["yscrollcommand"] = scroll_v.set

      # 保存ボタン
      sb4_frame = tk.Frame(self.sub_win)
      sb4_frame.grid(row=3, column=0, sticky=tk.NE)
      button = tk.Button(sb4_frame, text='保存', command=lambda:self.done())
      button.pack(padx=10, pady=10)
    elif self.sub_win != None and self.sub_win.winfo_exists():
      self.sub_win.lift()


  #-----------------------------------------------------------------
  # 予定追加ウィンドウで「保存」を押したときに呼び出されるメソッド
  #
  def done(self):
    # 日付
    days = '{}-{}-{}'.format(self.year, self.mon, self.today)
    print(days)

    # 種別
    kinds = self.combo.get()
    print(kinds)

    # 予定詳細
    memo = self.text.get("1.0", "end-1c")
    print(memo)

    # データベースに新規予定を挿入する
    connection = pymysql.connect(host='127.0.0.1',
                                user='root',
                              password='',
                               db='apr01',
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

    try:
        # トランザクション開始
        connection.begin()

        with connection.cursor() as cursor:
            cursor = connection.cursor()

            sql = "select * from schedule;"
            # SQLの実行
            cursor.execute(sql)


            resulsts = cursor.fetchall()
            for i, row in enumerate(resulsts):
                print(i, row)
        sql = "insert into schedule(days, kinds, memo) values('{}', '{}', '{}');".format(days, kinds, memo)
        print(sql)
        cursor.execute(sql)

        connection.commit()

    except Exception as e:
        print("error:", e)
        connection.rollback()
    finally:
        connection.close()

    self.sub_win.destroy()

  #-----------------------------------------------------------------
  # 日付をクリックした際に呼びだされるメソッド（コールバック関数）
  #
  # event: 左クリックイベント <Button-1>
  def click(self, event):
    day = event.widget['text']
    if day != ' ':
      print(day)
      self.title['text'] = '{}年{}月{}日の予定'.format(self.year, self.mon, day)
      self.today = day
      self.schedule()

  

def Main():
  root = tk.Tk()
  Yic(root)
  root.mainloop()

if __name__ == '__main__':
  Main()
