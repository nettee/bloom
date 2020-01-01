package model

import (
	"fmt"
	"io/ioutil"
	"testing"
)

const markdownFile string = "/Users/william/bloomstore/LeetCode 例题精讲/03-从二叉树遍历到回溯算法/03-从二叉树遍历到回溯算法.md"

func TestParser_show(t *testing.T) {
	byts, err := ioutil.ReadFile(markdownFile)
	if err != nil {
		panic(err)
	}
	content := string(byts)
	parser := NewParser(content)
	doc := parser.parse()
	showMarkdownDoc(&doc)
}

func showMarkdownDoc(doc *MarkdownDoc) {
	fmt.Printf("(title) %s\n", doc.title)
	for _, paragraph := range doc.body {
		fmt.Println("[Paragraph]")
		//fmt.Println()
		switch paragraph.(type) {
		case *Heading:
			headerLine := paragraph.(*Heading)
			fmt.Printf("(heading %d) %s", headerLine.level, headerLine.text)
		case *Image:
			imageLine := paragraph.(*Image)
			fmt.Printf("(image) %s", imageLine.caption)
		case *Quote:
			quote := paragraph.(*Quote)
			fmt.Println("(quote start)")
			fmt.Println(ParagraphString(quote))
			fmt.Print("(quote end)")
		case *CodeBlock:
			codeBlock := paragraph.(*CodeBlock)
			fmt.Printf("(code block) language: %s, %d lines", codeBlock.language, len(codeBlock.lines))
		case *MathBlock:
			mathBlock := paragraph.(*MathBlock)
			fmt.Printf("(math block) %d lines", len(mathBlock.lines))
		default:
			fmt.Print(ParagraphString(paragraph))
		}

		fmt.Println()
	}
}
