#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2016 kohei <nsshowdream@gmail.com>

from bs4 import BeautifulSoup
import csv
import sys
import requests
import MeCab

# リストを渡すとCSVファイルとして書き出してくれる関数
def writeCSV(list):
    f = open('output1.csv.csv', 'w')
    writer = csv.writer(f)
    writer.writerows(list)
    f.close()

# 単語がNeoglodに登録されていればTrue登録されていなければFalseを返す関数
def isExistNeoglod(text):
	mecabTagger = MeCab.Tagger("-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/")
	node = mecabTagger.parseToNode(text)
	morphemeCounter = 0
	morpheme = ''
	while node:
		featureList = node.feature.split(',')
		if featureList[0] == 'BOS/EOS':
			pass
		else:
			morpheme = str(featureList[1])
			morphemeCounter = morphemeCounter +1
		node = node.next

	# morphemeCounterが1で、かつmorphemeが固有名詞であれば、
	# 渡された語はNEologdに含まれていたと判断
	if morpheme=='固有名詞' and morphemeCounter==1 :
		return True
	else:
		return False

# URL先のHtmlを取得する関数
def getHtmlFromUrl(url):
	try:
		response = requests.get(url)
		html = response.text.encode(response.encoding)
		return html
	except:
		return 'error'

# Html内に含まれている本に関係したすべてのリンクを取得する関数
def getLinksFromPageHtml(pageHtml):
	soup = BeautifulSoup(pageHtml, "lxml")
	titles = soup.find_all('a',class_='taggedlink')
	links = []
	for title in titles:
		shortLink = title.get("href")
		link = 'http://ci.nii.ac.jp'+shortLink
		links.append(link)
	return links

# 詳細のHtmlから、よみがなを取得
def getKanaFromDetailHtml(detailHtml):
	soup = BeautifulSoup(detailHtml, "lxml")
	kanasWithNoise = soup.find_all('dl',class_='bblp-othertitle')
	kanasWithNoizeSize = len(kanasWithNoise)
	kanaWithNoise = ''
	# <dl class="bblp-othertitle">を取得したときに、
	# [タイトル読み]だけの場合と、[タイトル別名、タイトル読み]の場合の2通りがある。
	if kanasWithNoizeSize==1:
		kanaWithNoise = kanasWithNoise[0]
	elif kanasWithNoizeSize==2:
		kanaWithNoiseOtherName = kanasWithNoise[0]
		kanaWithNoise = kanasWithNoise[1]
	kana = ''
	try: kana = kanaWithNoise.p
	except: kana = 'error'
	kanaString = str(kana)
	kanaString = kanaString.replace('<p>','') # 読みがなの文字列から「<p>」を削除
	kanaString = kanaString.replace('</p>','') # 読みがなの文字列から「/<p>」を削除
	return kanaString

# 詳細のHtmlから、タイトルを取得
def getTitleFromDetailHtml(detailHtml):
	soup = BeautifulSoup(detailHtml, "lxml")
	titleWithNoise = soup.find('h1',class_='book_class')
	title = ''
	try: title = titleWithNoise.span
	except: title = 'error'
	titleString = str(title)
	titleString = titleString.replace('<span>','') # 読みがなの文字列から「<span>」を削除
	titleString = titleString.replace('</span>','') # 読みがなの文字列から「</span>」を削除
	return titleString

# メイン関数
def main():
	counter = 0
	pageCounter = 1
	books = []
	while pageCounter<=500:
		pageUrl = 'http://ci.nii.ac.jp/books/search?p='+str(pageCounter)+'&year_from=0&advanced=true&update_keep=true&count=20&sortorder=3&year_to=2016&type=1&lang1=jpn'
		pageHtml = getHtmlFromUrl(pageUrl)
		if pageHtml=='error':
			break
		links = getLinksFromPageHtml(pageHtml)
		for link in links:
			detailHtml = getHtmlFromUrl(link)
			if detailHtml=='error':
				break
			kana = getKanaFromDetailHtml(detailHtml)
			title = getTitleFromDetailHtml(detailHtml)
			neoglodFlag = isExistNeoglod(title)
			# 本のタイトルがNEologdに含まれていない場合
			if neoglodFlag == False:
				book = [title,kana]
				books.append(book)
				counter = counter + 1
				print str(pageCounter)+'ページ目,'+str(counter)+'項目目'
				print title
				print kana
				print '---------------------------------'
			# 本のタイトルがNEologdに含まれていた場合
			else:
				pass
			
		pageCounter = pageCounter + 1
	print 'ファイルに出力します'
	writeCSV(books)

if __name__ == '__main__':
    main()




