package main

import (
	"fmt"
	"github.com/urfave/cli/v2"
	"log"
	"os"
)

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
		Commands: [] *cli.Command{
			{
				Name:    "new",
				Aliases: [] string{"n"},
				Usage:   "create article or collection",
				Action: func(c *cli.Context) error {
					fmt.Println("new")
					return nil
				},
			},
			{
				Name:    "list",
				Aliases: [] string{"l"},
				Usage:   "list articles and collections",
				Action: func(c *cli.Context) error {
					fmt.Println("list")
					return nil
				},
			},
		},
	}

	err := app.Run(os.Args)
	if err != nil {
		log.Fatal(err)
	}
}
