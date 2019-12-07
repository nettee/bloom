package main

import (
	"fmt"
	"github.com/urfave/cli/v2"
	"io/ioutil"
	"log"
	"os"
	"strings"
)

const bloomStore = "/Users/william/bloomstore"

func listItems() error {
	items, err := ioutil.ReadDir(bloomStore)
	if err != nil {
		log.Fatal(err)
	}

	count := 0
	for _, item := range items {
		itemName := item.Name()
		if strings.HasPrefix(itemName, ".") {
			continue
		}
		fmt.Println(itemName)
		count += 1
	}
	fmt.Printf("%v articles(collections).\n", count)

	return nil
}

func main() {

	app := &cli.App {
		Name: "bloom",
		Version: "0.0.1",
		Authors: [] *cli.Author {
			{
				Name:  "nettee",
				Email: "nettee.liu@gmail.com",
			},
		},
		Usage: "Markdown article manager",
		Commands: [] *cli.Command {
			{
				Name:    "new",
				Aliases: [] string{"n"},
				Usage:   "create article or collection",
				Action: func(c *cli.Context) error {
					return nil
				},
			},
			{
				Name:    "list",
				Aliases: [] string{"l"},
				Usage:   "list articles and collections",
				Action: func(c *cli.Context) error {
					return listItems()
				},
			},
		},
	}

	err := app.Run(os.Args)
	if err != nil {
		log.Fatal(err)
	}
}
