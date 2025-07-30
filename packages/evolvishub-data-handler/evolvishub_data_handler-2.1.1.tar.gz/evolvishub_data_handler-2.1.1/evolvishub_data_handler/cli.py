"""Command-line interface for the data handler."""
import click
import signal
import sys
import yaml
import json
from loguru import logger

from .cdc_handler import CDCHandler
from .multi_cdc_handler import MultiCDCHandler
from .config_loader import load_config
from .config import SyncMode, MultiCDCConfig, FlexibleCDCConfig


@click.group()
def cli():
    """Data handler CLI."""
    pass


@cli.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
@click.option("--mode", "-m",
              type=click.Choice([mode.value for mode in SyncMode]),
              help="Sync mode (overrides config file setting)")
@click.option("--cron", help="Cron expression for scheduled sync (overrides config file setting)")
@click.option("--log-level", "-l",
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help="Log level")
@click.option("--log-file", help="Log file path")
def run(config, mode, cron, log_level, log_file):
    """Run data synchronization with specified mode."""
    try:
        # Configure logging
        logger.remove()  # Remove default handler
        logger.add(sys.stderr, level=log_level)
        if log_file:
            logger.add(log_file, level=log_level, rotation="10 MB", retention="10 days")

        # Load configuration
        config_data = load_config(config)

        # Override sync mode if specified
        if mode:
            config_data.sync.mode = SyncMode(mode)

        # Override cron expression if specified
        if cron:
            config_data.sync.cron_expression = cron
            config_data.sync.mode = SyncMode.CRON

        # Create handler
        handler = CDCHandler(config_data)

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received interrupt signal, stopping...")
            handler.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run based on mode
        logger.info(f"Starting sync in {config_data.sync.mode.value} mode...")
        handler.run()

    except Exception as e:
        logger.error(f"Error during sync: {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
@click.option("--log-level", "-l",
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help="Log level")
@click.option("--log-file", help="Log file path")
def sync(config, log_level, log_file):
    """Run a one-time sync (legacy command)."""
    try:
        # Configure logging
        logger.remove()
        logger.add(sys.stderr, level=log_level)
        if log_file:
            logger.add(log_file, level=log_level, rotation="10 MB", retention="10 days")

        config_data = load_config(config)
        config_data.sync.mode = SyncMode.ONE_TIME
        handler = CDCHandler(config_data)
        handler.sync()
    except Exception as e:
        logger.error(f"Error during sync: {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
@click.option("--log-level", "-l",
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help="Log level")
@click.option("--log-file", help="Log file path")
def continuous_sync(config, log_level, log_file):
    """Run continuous sync (legacy command)."""
    try:
        # Configure logging
        logger.remove()
        logger.add(sys.stderr, level=log_level)
        if log_file:
            logger.add(log_file, level=log_level, rotation="10 MB", retention="10 days")

        config_data = load_config(config)
        config_data.sync.mode = SyncMode.CONTINUOUS
        handler = CDCHandler(config_data)

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received interrupt signal, stopping...")
            handler.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        handler.run_continuous()
    except Exception as e:
        logger.error(f"Error during continuous sync: {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--config", "-c", required=True, help="Path to multi-CDC configuration file")
@click.option("--mapping", "-m", help="Run specific mapping only")
@click.option("--sequential", is_flag=True, help="Run mappings sequentially (overrides config)")
@click.option("--parallel", is_flag=True, help="Run mappings in parallel (overrides config)")
@click.option("--workers", type=int, help="Number of parallel workers (overrides config)")
@click.option("--log-level", "-l",
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help="Log level")
@click.option("--log-file", help="Log file path")
def run_multi(config, mapping, sequential, parallel, workers, log_level, log_file):
    """Run multi-source multi-destination CDC synchronization."""
    try:
        # Configure logging
        logger.remove()
        logger.add(sys.stderr, level=log_level)
        if log_file:
            logger.add(log_file, level=log_level, rotation="10 MB", retention="10 days")

        # Load multi-CDC configuration
        with open(config, 'r') as f:
            if config.endswith('.yaml') or config.endswith('.yml'):
                config_dict = yaml.safe_load(f)
            else:
                config_dict = json.load(f)

        multi_config = MultiCDCConfig(**config_dict)

        # Override execution settings if specified
        if sequential and parallel:
            raise click.ClickException("Cannot specify both --sequential and --parallel")

        if sequential:
            multi_config.parallel_execution = False
        elif parallel:
            multi_config.parallel_execution = True

        if workers:
            multi_config.max_workers = workers

        # Create multi-CDC handler
        handler = MultiCDCHandler(multi_config)

        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info("Received signal, stopping multi-CDC handler...")
            handler.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        if mapping:
            # Run specific mapping only
            logger.info(f"Running specific mapping: {mapping}")
            result = handler.execute_mapping(mapping)

            if result.success:
                logger.info(f"Mapping {mapping} completed successfully: {result.records_processed} records in {result.duration_seconds:.2f}s")
            else:
                logger.error(f"Mapping {mapping} failed: {result.error}")
                sys.exit(1)
        else:
            # Run all mappings continuously
            logger.info("Starting continuous multi-CDC synchronization...")
            handler.run_continuous()

    except Exception as e:
        logger.error(f"Error during multi-CDC sync: {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--config", "-c", required=True, help="Path to multi-CDC configuration file")
@click.option("--format", "-f",
              type=click.Choice(['table', 'json', 'yaml']),
              default='table', help="Output format")
def status(config, format):
    """Show status of multi-CDC mappings."""
    try:
        # Load configuration
        with open(config, 'r') as f:
            if config.endswith('.yaml') or config.endswith('.yml'):
                config_dict = yaml.safe_load(f)
            else:
                config_dict = json.load(f)

        multi_config = MultiCDCConfig(**config_dict)
        handler = MultiCDCHandler(multi_config)

        # Get status
        summary = handler.get_summary()
        mapping_status = handler.get_mapping_status()

        if format == 'json':
            output = {
                'summary': summary,
                'mappings': mapping_status
            }
            click.echo(json.dumps(output, indent=2, default=str))

        elif format == 'yaml':
            output = {
                'summary': summary,
                'mappings': mapping_status
            }
            click.echo(yaml.dump(output, default_flow_style=False))

        else:  # table format
            click.echo(f"\n=== Multi-CDC Status: {summary['config_name']} ===")
            click.echo(f"Total mappings: {summary['total_mappings']}")
            click.echo(f"Enabled mappings: {summary['enabled_mappings']}")
            click.echo(f"Total executions: {summary['total_executions']}")
            click.echo(f"Successful executions: {summary['successful_executions']}")
            click.echo(f"Failed executions: {summary['failed_executions']}")
            click.echo(f"Total records processed: {summary['total_records_processed']}")
            click.echo(f"Average duration: {summary['average_duration_seconds']}s")
            click.echo(f"Currently running: {summary['is_running']}")

            click.echo(f"\n=== Mapping Details ===")
            for mapping in mapping_status:
                status_icon = "✓" if mapping['enabled'] else "✗"
                click.echo(f"{status_icon} {mapping['name']}")
                click.echo(f"  Source: {mapping['source_type']} -> {mapping['source_table']}")
                click.echo(f"  Destination: {mapping['destination_type']} -> {mapping['destination_table']}")
                click.echo(f"  Executions: {mapping['total_executions']}")

                if mapping['last_execution']:
                    last = mapping['last_execution']
                    success_icon = "✓" if last['success'] else "✗"
                    click.echo(f"  Last run: {success_icon} {last['timestamp']} ({last['records_processed']} records, {last['duration_seconds']:.2f}s)")
                    if last['error']:
                        click.echo(f"  Error: {last['error']}")
                else:
                    click.echo(f"  Last run: Never")
                click.echo()

    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--config", "-c", required=True, help="Path to multi-CDC configuration file")
@click.option("--mapping", "-m", required=True, help="Mapping name to execute")
@click.option("--log-level", "-l",
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help="Log level")
def run_mapping(config, mapping, log_level):
    """Run a single mapping from multi-CDC configuration."""
    try:
        # Configure logging
        logger.remove()
        logger.add(sys.stderr, level=log_level)

        # Load configuration
        with open(config, 'r') as f:
            if config.endswith('.yaml') or config.endswith('.yml'):
                config_dict = yaml.safe_load(f)
            else:
                config_dict = json.load(f)

        multi_config = MultiCDCConfig(**config_dict)
        handler = MultiCDCHandler(multi_config)

        # Execute specific mapping
        result = handler.execute_mapping(mapping)

        if result.success:
            click.echo(f"✓ Mapping '{mapping}' completed successfully")
            click.echo(f"  Records processed: {result.records_processed}")
            click.echo(f"  Duration: {result.duration_seconds:.2f} seconds")
        else:
            click.echo(f"✗ Mapping '{mapping}' failed: {result.error}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error running mapping: {str(e)}")
        raise click.ClickException(str(e))


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()